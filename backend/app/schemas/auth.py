import re
import datetime
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional

class UserRegisterRequest(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "UserRegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: str
    role: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
