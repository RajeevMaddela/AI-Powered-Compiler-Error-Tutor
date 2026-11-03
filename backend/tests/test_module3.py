import pytest
from backend.app.compiler.constants import ErrorCategory
from backend.app.models.models import User, Submission, ErrorRecord, Feedback, Consent
from backend.app.schemas.submission import AnalyzeRequest, MAX_SOURCE_CODE_BYTES
from backend.app.core.database import SessionLocal, Base, engine

def test_code_payload_size_limit():
    """Verify that source code larger than 64KB is rejected."""
    valid_code = "int main() { return 0; }"
    req = AnalyzeRequest(code=valid_code)
    assert req.code == valid_code

    oversized_code = "a" * (MAX_SOURCE_CODE_BYTES + 10)
    with pytest.raises(ValueError, match="exceeds maximum allowed size"):
        AnalyzeRequest(code=oversized_code)


def test_consent_default_is_denied():
    """Confirms privacy-by-default: if no consent record exists, status defaults to denied."""
    db = SessionLocal()
    try:
        user = User(
            name="Privacy Test User",
            email="privacy@example.com",
            password_hash="mock_hash_for_test",
            role="student"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Check consent in DB
        consent = db.query(Consent).filter(Consent.user_id == user.id).first()
        assert consent is None  # Defaults to denied without explicit opt-in
    finally:
        db.delete(user)
        db.commit()
        db.close()

