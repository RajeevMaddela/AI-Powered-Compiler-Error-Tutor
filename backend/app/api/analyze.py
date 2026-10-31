import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.rate_limit import analyze_rate_limiter
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Submission, ErrorRecord
from backend.app.schemas.submission import AnalyzeRequest, AnalyzeResponse, DiagnosticItem
from backend.app.sandbox.runner import run_code_in_sandbox
from backend.app.compiler.parser import parse_compiler_output

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Compiler Analysis"])

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_code(
    req: AnalyzeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Enforce rate limit per user
    user_key = f"user_{current_user.id}"
    if not analyze_rate_limiter.is_allowed(user_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many analysis requests. Please wait a moment before analyzing again."
        )

    # Sanitize / ensure valid input
    code = req.code

    # Execute inside isolated sandbox
    sandbox_res = run_code_in_sandbox(code)

    # Determine compile status
    if sandbox_res.timed_out:
        compile_status = "timeout"
    elif sandbox_res.exit_code == 0:
        compile_status = "clean"
    else:
        compile_status = "error"

    # Parse compiler text
    parsed_diagnostics = parse_compiler_output(sandbox_res.output)

    # Persist submission in database (without exposing source code in logs)
    submission = Submission(
        user_id=current_user.id,
        code=code,
        compile_status=compile_status,
        duration_ms=sandbox_res.duration_ms
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    diagnostic_items = []
    for diag in parsed_diagnostics:
        err_rec = ErrorRecord(
            submission_id=submission.id,
            line=diag.line,
            column=diag.column,
            severity=diag.severity,
            raw_message=diag.message,
            category=None,       # Populated in Module 2
            confidence=None,     # Populated in Module 2
            is_primary=diag.is_primary,
            abstained=False,
            model_version=None
        )
        db.add(err_rec)
        db.commit()
        db.refresh(err_rec)

        diagnostic_items.append(DiagnosticItem(
            id=err_rec.id,
            line=diag.line,
            column=diag.column,
            severity=diag.severity,
            message=diag.message,
            notes=diag.notes,
            is_primary=diag.is_primary,
            is_follow_on=diag.is_follow_on,
            category=None,
            confidence=None,
            abstained=False
        ))

    logger.info("Submission %d processed for user %d (status: %s, duration: %d ms, errors: %d)",
                submission.id, current_user.id, compile_status, sandbox_res.duration_ms, len(diagnostic_items))

    return AnalyzeResponse(
        submission_id=submission.id,
        compile_status=compile_status,
        duration_ms=sandbox_res.duration_ms,
        errors=diagnostic_items,
        raw_compiler_output=sandbox_res.output
    )
