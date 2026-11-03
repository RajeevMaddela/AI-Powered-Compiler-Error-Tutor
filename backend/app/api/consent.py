import logging
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Consent
from backend.app.schemas.consent import ConsentUpdate, ConsentResponse

logger = logging.getLogger("tutor_api.consent")
router = APIRouter(prefix="/api/consent", tags=["Consent"])

@router.get("", response_model=ConsentResponse)
def get_user_consent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the student's current retraining consent status.
    Default is 'denied' (privacy-by-default).
    """
    consent = db.query(Consent).filter(Consent.user_id == current_user.id).order_by(Consent.decided_at.desc()).first()
    if not consent:
        return ConsentResponse(
            id=None,
            user_id=current_user.id,
            decision="denied",
            round_id=None,
            decided_at=datetime.datetime.utcnow()
        )
    return consent


@router.post("", response_model=ConsentResponse)
def update_user_consent(
    payload: ConsentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the student's retraining consent decision with an immutable audit timestamp.
    """
    consent = db.query(Consent).filter(Consent.user_id == current_user.id).first()
    if not consent:
        consent = Consent(
            user_id=current_user.id,
            round_id=payload.round_id,
            decision=payload.decision,
            decided_at=datetime.datetime.utcnow()
        )
        db.add(consent)
    else:
        consent.decision = payload.decision
        consent.round_id = payload.round_id
        consent.decided_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(consent)
    logger.info("User %d updated consent decision to '%s'", current_user.id, payload.decision)
    return consent

