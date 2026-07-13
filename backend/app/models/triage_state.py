from __future__ import annotations

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class TriageCategory(str, Enum):
    clinical = "clinical"
    operational = "operational"


class TriageUrgency(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TriageStatus(str, Enum):
    pending = "pending"
    approved = "approved"


class TriageState(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    raw_text: str
    category: TriageCategory | None = None
    urgency: TriageUrgency | None = None
    status: TriageStatus = TriageStatus.pending
    queue_name: str | None = None
