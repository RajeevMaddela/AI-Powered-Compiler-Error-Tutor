import logging
from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, List

from backend.app.core.database import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Submission, ErrorRecord, ModelVersion
from backend.app.schemas.analytics import (
    DashboardStats, CategoryMetric, TimelinePoint, RecentMistake
)
from ml.pipeline.classifier import get_classifier

logger = logging.getLogger("tutor_api.analytics")
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes analytical insights and mistake trends for the authenticated student.
    """
    submissions = (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.asc())
        .all()
    )

    total_submissions = len(submissions)
    clean_compiles = sum(1 for s in submissions if s.compile_status == "clean")
    error_compiles = total_submissions - clean_compiles
    success_rate = round((clean_compiles / total_submissions * 100), 1) if total_submissions > 0 else 0.0

    # Collect errors
    sub_ids = [s.id for s in submissions]
    errors = (
        db.query(ErrorRecord)
        .filter(ErrorRecord.submission_id.in_(sub_ids))
        .all()
        if sub_ids else []
    )

    total_errors_diagnosed = len(errors)

    # Category breakdown
    cat_counts: Dict[str, int] = defaultdict(int)
    for err in errors:
        c = err.category or "ABSTAINED"
        cat_counts[c] += 1

    categories_breakdown = [
        CategoryMetric(
            category=cat,
            count=cnt,
            percentage=round((cnt / total_errors_diagnosed * 100), 1) if total_errors_diagnosed > 0 else 0.0
        )
        for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    # Mistakes timeline (grouped by date)
    timeline_dict = defaultdict(lambda: {"total": 0, "clean": 0, "error": 0})
    for sub in submissions:
        date_str = sub.created_at.strftime("%Y-%m-%d")
        timeline_dict[date_str]["total"] += 1
        if sub.compile_status == "clean":
            timeline_dict[date_str]["clean"] += 1
        else:
            timeline_dict[date_str]["error"] += 1

    mistakes_timeline = [
        TimelinePoint(
            date=d,
            total_submissions=vals["total"],
            clean_count=vals["clean"],
            error_count=vals["error"]
        )
        for d, vals in sorted(timeline_dict.items())
    ]

    # Recent mistakes (latest 10 primary errors)
    recent_errors = (
        db.query(ErrorRecord, Submission.created_at)
        .join(Submission, ErrorRecord.submission_id == Submission.id)
        .filter(Submission.user_id == current_user.id)
        .order_by(ErrorRecord.id.desc())
        .limit(10)
        .all()
    )

    recent_mistakes = [
        RecentMistake(
            submission_id=err.submission_id,
            error_id=err.id,
            category=err.category or "UNKNOWN",
            line=err.line,
            severity=err.severity,
            raw_message=err.raw_message,
            created_at=created_at
        )
        for err, created_at in recent_errors
    ]

    # Active model version
    active_mv = db.query(ModelVersion).filter(ModelVersion.active == True).first()
    active_version = active_mv.version if active_mv else get_classifier().version

    return DashboardStats(
        total_submissions=total_submissions,
        clean_compiles=clean_compiles,
        error_compiles=error_compiles,
        success_rate=success_rate,
        total_errors_diagnosed=total_errors_diagnosed,
        categories_breakdown=categories_breakdown,
        mistakes_timeline=mistakes_timeline,
        recent_mistakes=recent_mistakes,
        active_model_version=active_version
    )

