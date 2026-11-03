import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.api.auth import get_current_user, COOKIE_NAME
from backend.app.models.models import User, Submission, Consent, ModelVersion
from backend.app.schemas.auth import MessageResponse
from backend.app.schemas.account import UserProfileResponse
from ml.pipeline.classifier import get_classifier

logger = logging.getLogger("tutor_api.account")
router = APIRouter(prefix="/api/account", tags=["Account"])

@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns user profile details, submission statistics, consent status, and current active ML model version.
    """
    total_submissions = db.query(Submission).filter(Submission.user_id == current_user.id).count()

    consent = db.query(Consent).filter(Consent.user_id == current_user.id).order_by(Consent.decided_at.desc()).first()
    consent_decision = consent.decision if consent else "denied"

    active_mv = db.query(ModelVersion).filter(ModelVersion.active == True).first()
    active_version = active_mv.version if active_mv else get_classifier().version

    return UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
        total_submissions=total_submissions,
        consent_decision=consent_decision,
        active_model_version=active_version
    )


@router.post("/clear-history", response_model=MessageResponse)
def clear_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes all submissions and diagnosed errors belonging to the current user,
    leaving the user account intact.
    """
    subs = db.query(Submission).filter(Submission.user_id == current_user.id).all()
    count = len(subs)
    for s in subs:
        db.delete(s)
    db.commit()
    logger.info("Cleared %d submissions for user %d", count, current_user.id)
    return {"message": f"Successfully deleted {count} submission records."}


@router.delete("", response_model=MessageResponse)
def delete_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes the current user's account and all associated submissions/data (cascade).
    Clears the session cookie.
    """
    user_id = current_user.id
    db.delete(current_user)
    db.commit()
    response.delete_cookie(key=COOKIE_NAME)
    logger.info("Permanently deleted user %d and all associated records", user_id)
    return {"message": "Your account and all associated data have been deleted permanently."}
