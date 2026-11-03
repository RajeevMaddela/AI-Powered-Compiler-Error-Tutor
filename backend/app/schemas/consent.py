from pydantic import BaseModel, field_validator
from typing import Optional
import datetime

VALID_DECISIONS = {"granted", "denied", "pending"}

class ConsentUpdate(BaseModel):
    decision: str
    round_id: Optional[int] = None

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        lowered = v.lower().strip()
        if lowered not in VALID_DECISIONS:
            raise ValueError(f"Decision must be one of: {sorted(list(VALID_DECISIONS))}")
        return lowered


class ConsentResponse(BaseModel):
    id: Optional[int] = None
    user_id: int
    decision: str
    round_id: Optional[int] = None
    decided_at: datetime.datetime

    class Config:
        from_attributes = True

