from pydantic import BaseModel
from typing import Optional
import datetime

class UserProfileResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: str
    role: str
    created_at: datetime.datetime
    total_submissions: int
    consent_decision: str
    active_model_version: str

    class Config:
        from_attributes = True

