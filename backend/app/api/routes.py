from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.api.guardrails import enforce_rate_limit, client_ip
from app.core.config import settings
from app.db import approve_request, delete_request_from_db, get_audit_log, get_queue, get_request, log_audit_event, save_request
from app.graph import build_triage_graph
from app.models import ApproveRequest, AuditLogItem, QueueItem, SubmitRequest, TriageState, TriageCategory

router = APIRouter()
triage_graph = build_triage_graph()


def verify_staff_token(x_staff_token: str | None = Header(None, alias="X-Staff-Token")) -> None:
    if not x_staff_token or x_staff_token != settings.staff_token:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid staff token")


@router.post("/submit-request", response_model=QueueItem)
def submit_request(payload: SubmitRequest, request: Request) -> QueueItem:
    enforce_rate_limit(request, "submit")
    initial_state = TriageState(raw_text=payload.raw_text)
    classified_state = triage_graph.invoke(initial_state)
    triage_state = TriageState.model_validate(classified_state)

    if triage_state.category == TriageCategory.operational:
        raise HTTPException(
            status_code=400,
            detail="Submission rejected: Only clinical or medical inquiries are accepted."
        )

    saved = save_request(triage_state)
    log_audit_event(
        "submit_request",
        saved.request_id,
        client_ip(request),
        {
            "category": saved.category.value if saved.category else None,
            "urgency": saved.urgency.value if saved.urgency else None,
            "status": saved.status.value,
            "queue_name": saved.queue_name,
        },
    )
    return saved


@router.get("/queue", response_model=list[QueueItem])
def read_queue(x_staff_token: str | None = Depends(verify_staff_token)) -> list[QueueItem]:
    return get_queue()


@router.get("/request-status/{request_id}", response_model=QueueItem)
def read_request_status(request_id: str) -> QueueItem:
    try:
        uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Request not found")

    item = get_request(request_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return item


@router.get("/audit-log", response_model=list[AuditLogItem])
def read_audit_log(x_staff_token: str | None = Depends(verify_staff_token)) -> list[AuditLogItem]:
    return get_audit_log()


@router.post("/approve-request", response_model=QueueItem)
def approve_triage_request(
    payload: ApproveRequest,
    request: Request,
    x_staff_token: str | None = Depends(verify_staff_token),
) -> QueueItem:
    enforce_rate_limit(request, "approve")
    updated = approve_request(payload.request_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Request not found")
    log_audit_event(
        "approve_request",
        updated.request_id,
        client_ip(request),
        {
            "status": updated.status.value,
            "queue_name": updated.queue_name,
        },
    )
    return updated


@router.delete("/request/{request_id}", response_model=dict)
def delete_triage_request(
    request_id: str,
    request: Request,
    x_staff_token: str | None = Depends(verify_staff_token),
) -> dict:
    try:
        uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")

    success = delete_request_from_db(request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")

    log_audit_event(
        "delete_request",
        request_id,
        client_ip(request),
        {
            "deleted_at": uuid.uuid4().hex,  # Dummy value or details
        },
    )
    return {"status": "success", "message": f"Request {request_id} deleted successfully"}
