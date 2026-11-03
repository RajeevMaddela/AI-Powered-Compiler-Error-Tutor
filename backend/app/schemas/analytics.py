from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime

class CategoryMetric(BaseModel):
    category: str
    count: int
    percentage: float

class TimelinePoint(BaseModel):
    date: str
    total_submissions: int
    clean_count: int
    error_count: int

class RecentMistake(BaseModel):
    submission_id: int
    error_id: int
    category: str
    line: Optional[int] = None
    severity: str
    raw_message: str
    created_at: datetime.datetime

class DashboardStats(BaseModel):
    total_submissions: int
    clean_compiles: int
    error_compiles: int
    success_rate: float
    total_errors_diagnosed: int
    categories_breakdown: List[CategoryMetric]
    mistakes_timeline: List[TimelinePoint]
    recent_mistakes: List[RecentMistake]
    active_model_version: str

