from __future__ import annotations

from datetime import datetime, timezone
from contextlib import contextmanager
import json

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.core.config import settings
from app.models.api import AuditLogItem, QueueItem
from app.models.triage_state import TriageCategory, TriageState, TriageStatus, TriageUrgency

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS triage_requests (
    request_id TEXT PRIMARY KEY,
    raw_text TEXT NOT NULL,
    category TEXT,
    urgency TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    queue_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

AUDIT_SCHEMA = """
CREATE TABLE IF NOT EXISTS triage_audit_log (
    id BIGSERIAL PRIMARY KEY,
    action TEXT NOT NULL,
    request_id TEXT,
    actor_ip TEXT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""


@contextmanager
def get_connection():
    connection = psycopg.connect(settings.database_url, row_factory=dict_row)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(DB_SCHEMA)
        connection.execute(AUDIT_SCHEMA)


def seed_dummy_data() -> None:
    with get_connection() as connection:
        count = connection.execute("SELECT COUNT(*) AS count FROM triage_requests").fetchone()["count"]
        if count:
            return

        seed_rows = [
            TriageState(raw_text="Need a prescription refill", category=TriageCategory.clinical, urgency=TriageUrgency.P2),
            TriageState(raw_text="Question about a billing invoice", category=TriageCategory.operational, urgency=TriageUrgency.P3),
            TriageState(raw_text="Severe chest pain and shortness of breath", category=TriageCategory.clinical, urgency=TriageUrgency.P1),
        ]
        for item in seed_rows:
            queue_name = "Clinical Queue" if item.category == TriageCategory.clinical else "Operations Queue"
            connection.execute(
                """
                INSERT INTO triage_requests
                (request_id, raw_text, category, urgency, status, queue_name, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (request_id) DO UPDATE SET
                  raw_text = EXCLUDED.raw_text,
                  category = EXCLUDED.category,
                  urgency = EXCLUDED.urgency,
                  status = EXCLUDED.status,
                  queue_name = EXCLUDED.queue_name,
                  created_at = EXCLUDED.created_at
                """,
                (
                    item.request_id,
                    item.raw_text,
                    item.category.value if item.category else None,
                    item.urgency.value if item.urgency else None,
                    item.status.value,
                    queue_name,
                    datetime.now(timezone.utc),
                ),
            )


def save_request(state: TriageState) -> QueueItem:
    created_at = datetime.now(timezone.utc)
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO triage_requests
            (request_id, raw_text, category, urgency, status, queue_name, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                state.request_id,
                state.raw_text,
                state.category.value if state.category else None,
                state.urgency.value if state.urgency else None,
                state.status.value,
                state.queue_name,
                created_at,
            ),
        )
    return QueueItem(
        request_id=state.request_id,
        raw_text=state.raw_text,
        category=state.category,
        urgency=state.urgency,
        status=state.status,
        queue_name=state.queue_name,
        created_at=created_at,
    )


def get_queue() -> list[QueueItem]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT request_id, raw_text, category, urgency, status, queue_name, created_at FROM triage_requests ORDER BY created_at DESC"
        ).fetchall()

    return [
        QueueItem(
            request_id=row["request_id"],
            raw_text=row["raw_text"],
            category=TriageCategory(row["category"]) if row["category"] else None,
            urgency=TriageUrgency(row["urgency"]) if row["urgency"] else None,
            status=TriageStatus(row["status"]),
            queue_name=row["queue_name"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def get_request(request_id: str) -> QueueItem | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT request_id, raw_text, category, urgency, status, queue_name, created_at FROM triage_requests WHERE request_id = %s",
            (request_id,),
        ).fetchone()

    if row is None:
        return None

    return QueueItem(
        request_id=row["request_id"],
        raw_text=row["raw_text"],
        category=TriageCategory(row["category"]) if row["category"] else None,
        urgency=TriageUrgency(row["urgency"]) if row["urgency"] else None,
        status=TriageStatus(row["status"]),
        queue_name=row["queue_name"],
        created_at=row["created_at"],
    )


def approve_request(request_id: str) -> QueueItem | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT request_id, raw_text, category, urgency, status, queue_name, created_at FROM triage_requests WHERE request_id = %s",
            (request_id,),
        ).fetchone()
        if row is None:
            return None

        updated_row = connection.execute(
            "UPDATE triage_requests SET status = %s WHERE request_id = %s RETURNING request_id, raw_text, category, urgency, status, queue_name, created_at",
            (TriageStatus.approved.value, request_id),
        ).fetchone()

    return QueueItem(
        request_id=updated_row["request_id"],
        raw_text=updated_row["raw_text"],
        category=TriageCategory(updated_row["category"]) if updated_row["category"] else None,
        urgency=TriageUrgency(updated_row["urgency"]) if updated_row["urgency"] else None,
        status=TriageStatus(updated_row["status"]),
        queue_name=updated_row["queue_name"],
        created_at=updated_row["created_at"],
    )


def log_audit_event(action: str, request_id: str | None, actor_ip: str | None, details: dict) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO triage_audit_log (action, request_id, actor_ip, details)
            VALUES (%s, %s, %s, %s::jsonb)
            """,
            (action, request_id, actor_ip, Json(details)),
        )


def get_audit_log(limit: int = 50) -> list[AuditLogItem]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, action, request_id, actor_ip, details, created_at
            FROM triage_audit_log
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()

    return [
        AuditLogItem(
            id=row["id"],
            action=row["action"],
            request_id=row["request_id"],
            actor_ip=row["actor_ip"],
            details=row["details"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def delete_request_from_db(request_id: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT request_id FROM triage_requests WHERE request_id = %s",
            (request_id,),
        ).fetchone()
        if row is None:
            return False

        connection.execute(
            "DELETE FROM triage_requests WHERE request_id = %s",
            (request_id,),
        )
    return True
