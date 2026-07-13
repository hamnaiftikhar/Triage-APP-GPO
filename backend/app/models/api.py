from __future__ import annotations

from datetime import datetime

import html
from pydantic import BaseModel, Field, field_validator

from .triage_state import TriageCategory, TriageStatus, TriageUrgency


class SubmitRequest(BaseModel):
    raw_text: str = Field(min_length=1, max_length=2000)

    @field_validator("raw_text")
    @classmethod
    def validate_and_sanitize_raw_text(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Request text cannot be empty or only spaces")
        return html.escape(stripped)


class ApproveRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=64)


class QueueItem(BaseModel):
    request_id: str
    raw_text: str
    category: TriageCategory | None = None
    urgency: TriageUrgency | None = None
    status: TriageStatus = TriageStatus.pending
    queue_name: str | None = None
    created_at: datetime


class AuditLogItem(BaseModel):
    id: int
    action: str
    request_id: str | None = None
    actor_ip: str | None = None
    details: dict
    created_at: datetime
