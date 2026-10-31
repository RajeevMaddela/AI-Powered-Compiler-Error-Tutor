from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_user, COOKIE_NAME
from backend.app.models.models import User
from backend.app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/account", tags=["Account"])

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
    db.delete(current_user)
    db.commit()
    response.delete_cookie(key=COOKIE_NAME)
    return {"message": "Your account and all associated data have been deleted permanently."}
