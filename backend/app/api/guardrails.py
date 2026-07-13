from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import HTTPException, Request

SUBMIT_LIMIT = 10
APPROVE_LIMIT = 30
WINDOW_SECONDS = 60

_rate_store: dict[tuple[str, str], deque[datetime]] = defaultdict(deque)
_rate_lock = Lock()


def client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def enforce_rate_limit(request: Request, action: str) -> None:
    limit = SUBMIT_LIMIT if action == "submit" else APPROVE_LIMIT
    key = (client_ip(request), action)
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=WINDOW_SECONDS)

    with _rate_lock:
        bucket = _rate_store[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded for {action}")
        bucket.append(now)
