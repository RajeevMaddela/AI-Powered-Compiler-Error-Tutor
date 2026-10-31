from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Submission, ErrorRecord
from backend.app.schemas.submission import SubmissionSummary, SubmissionDetail, DiagnosticItem
from backend.app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/history", tags=["Submission History"])

@router.get("", response_model=List[SubmissionSummary])
def get_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns list of submissions belonging strictly to the authenticated user.
    """
    submissions = (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(desc(Submission.created_at))
        .limit(100)
        .all()
    )

    summaries = []
    for sub in submissions:
        err_count = sum(1 for e in sub.errors if e.severity in ("error", "fatal error"))
        warn_count = sum(1 for e in sub.errors if e.severity == "warning")
        summaries.append(SubmissionSummary(
            id=sub.id,
            created_at=sub.created_at,
            compile_status=sub.compile_status,
            duration_ms=sub.duration_ms,
            error_count=err_count,
            warning_count=warn_count
        ))

    return summaries


@router.get("/{submission_id}", response_model=SubmissionDetail)
def get_submission_detail(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves a specific submission. Returns 404/403 if it does not belong to the user.
    """
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found."
        )

    # Multi-tenant isolation: strictly verify ownership
    if sub.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to view this submission."
        )

    errors = [
        DiagnosticItem(
            id=e.id,
            line=e.line,
            column=e.column,
            severity=e.severity,
            message=e.raw_message,
            notes=[],
            is_primary=e.is_primary,
            is_follow_on=not e.is_primary,
            category=e.category,
            confidence=e.confidence,
            abstained=e.abstained
        )
        for e in sub.errors
    ]

    return SubmissionDetail(
        id=sub.id,
        code=sub.code,
        created_at=sub.created_at,
        compile_status=sub.compile_status,
        duration_ms=sub.duration_ms,
        errors=errors
    )


@router.delete("/{submission_id}", response_model=MessageResponse)
def delete_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific submission. Prevents deleting other users' submissions.
    """
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found."
        )

    if sub.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to delete this submission."
        )

    db.delete(sub)
    db.commit()
    return {"message": "Submission deleted successfully."}


@router.delete("", response_model=MessageResponse)
def delete_all_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes all submission history belonging to the authenticated user.
    """
    db.query(Submission).filter(Submission.user_id == current_user.id).delete()
    db.commit()
    return {"message": "All your history has been cleared successfully."}
