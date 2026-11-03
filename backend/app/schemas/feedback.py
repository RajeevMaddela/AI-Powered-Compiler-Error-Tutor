from pydantic import BaseModel, field_validator
from typing import Optional
import datetime
from backend.app.compiler.constants import ErrorCategory

VALID_CATEGORIES = {c.value for c in ErrorCategory}

class FeedbackCreate(BaseModel):
    error_id: int
    helpful: bool
    corrected_category: Optional[str] = None

    @field_validator("corrected_category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "" and v not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{v}'. Must be one of: {sorted(list(VALID_CATEGORIES))}")
        return v or None


class FeedbackResponse(BaseModel):
    id: int
    error_id: int
    helpful: bool
    corrected_category: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

