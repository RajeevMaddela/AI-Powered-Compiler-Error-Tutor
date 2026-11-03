from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
import datetime

MAX_SOURCE_CODE_BYTES = 64 * 1024  # 64 KB

class AnalyzeRequest(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def validate_code_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("C++ source code cannot be empty")
        if len(v.encode("utf-8")) > MAX_SOURCE_CODE_BYTES:
            raise ValueError(f"Source code exceeds maximum allowed size of {MAX_SOURCE_CODE_BYTES // 1024} KB")
        return v


class ExplanationItem(BaseModel):
    title: str
    summary: str
    what_happened: str
    where: str
    how_to_fix: List[str]
    example_wrong: str
    example_fixed: str


class DiagnosticItem(BaseModel):
    id: Optional[int] = None
    line: Optional[int] = None
    column: Optional[int] = None
    severity: str
    message: str
    notes: List[str] = []
    is_primary: bool = False
    is_follow_on: bool = False
    category: Optional[str] = None
    confidence: Optional[float] = None
    abstained: bool = False
    model_version: Optional[str] = None
    explanation: Optional[ExplanationItem] = None

    class Config:
        from_attributes = True


class AnalyzeResponse(BaseModel):
    submission_id: int
    compile_status: str
    duration_ms: int
    errors: List[DiagnosticItem]
    raw_compiler_output: str


class SubmissionSummary(BaseModel):
    id: int
    created_at: datetime.datetime
    compile_status: str
    duration_ms: int
    error_count: int
    warning_count: int

    class Config:
        from_attributes = True


class SubmissionDetail(BaseModel):
    id: int
    code: str
    created_at: datetime.datetime
    compile_status: str
    duration_ms: int
    errors: List[DiagnosticItem]

    class Config:
        from_attributes = True
