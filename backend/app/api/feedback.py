import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, ErrorRecord, Feedback, Submission
from backend.app.schemas.feedback import FeedbackCreate, FeedbackResponse

logger = logging.getLogger("tutor_api.feedback")
router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits student feedback (helpful boolean and optional corrected category) for a specific diagnostic error.
    Strictly enforces multi-tenant ownership: the error must belong to one of the student's submissions.
    """
    # Verify error exists
    error = db.query(ErrorRecord).join(Submission).filter(
        ErrorRecord.id == payload.error_id,
        Submission.user_id == current_user.id
    ).first()

    if not error:
        # Check if error exists at all to differentiate 403 vs 404
        any_error = db.query(ErrorRecord).filter(ErrorRecord.id == payload.error_id).first()
        if any_error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you cannot submit feedback for another user's error."
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error record not found."
        )

    # Check if feedback already exists for this error by this user; update if so
    existing_feedback = db.query(Feedback).filter(Feedback.error_id == error.id).first()
    if existing_feedback:
        existing_feedback.helpful = payload.helpful
        existing_feedback.corrected_category = payload.corrected_category
        db.commit()
        db.refresh(existing_feedback)
        logger.info("Updated feedback for error %d by user %d (helpful=%s)", error.id, current_user.id, payload.helpful)
        return existing_feedback

    new_feedback = Feedback(
        error_id=error.id,
        helpful=payload.helpful,
        corrected_category=payload.corrected_category
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    logger.info("Created feedback for error %d by user %d (helpful=%s)", error.id, current_user.id, payload.helpful)
    return new_feedback


@router.get("/submission/{submission_id}", response_model=List[FeedbackResponse])
def get_submission_feedback(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all feedback submitted for errors in a given submission.
    """
    sub = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.user_id == current_user.id
    ).first()

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or unauthorized."
        )

    feedbacks = db.query(Feedback).join(ErrorRecord).filter(
        ErrorRecord.submission_id == sub.id
    ).all()

    return feedbacks

