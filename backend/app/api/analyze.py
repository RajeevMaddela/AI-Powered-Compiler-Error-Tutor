import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.rate_limit import analyze_rate_limiter
from backend.app.api.auth import get_current_user
from backend.app.models.models import User, Submission, ErrorRecord
from backend.app.schemas.submission import AnalyzeRequest, AnalyzeResponse, DiagnosticItem, ExplanationItem
from backend.app.sandbox.runner import run_code_in_sandbox
from backend.app.compiler.parser import parse_compiler_output
from ml.pipeline.classifier import get_classifier
from ml.pipeline.explanations import generate_explanation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Compiler Analysis"])


def extract_source_stdlib_flags(source: str) -> Dict[str, bool]:
    lines = source.splitlines()
    return {
        "has_include_iostream": any("#include <iostream>" in l for l in lines),
        "has_include_vector": any("#include <vector>" in l for l in lines),
        "has_include_string": any("#include <string>" in l for l in lines),
        "has_include_map": any("#include <map>" in l for l in lines),
        "has_using_namespace_std": any("using namespace std;" in l for l in lines),
        "uses_std_prefix": any("std::" in l for l in lines),
    }


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

    # Parse compiler text into structured diagnostic records
    parsed_diagnostics = parse_compiler_output(sandbox_res.output)

    # Persist submission in database
    submission = Submission(
        user_id=current_user.id,
        code=code,
        compile_status=compile_status,
        duration_ms=sandbox_res.duration_ms
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Initialize classifier
    classifier = get_classifier()
    stdlib_flags = extract_source_stdlib_flags(code)
    total_errors = sum(1 for d in parsed_diagnostics if d.severity in ("error", "fatal error"))
    total_followons = sum(1 for d in parsed_diagnostics if d.is_follow_on)

    diagnostic_items = []
    for diag in parsed_diagnostics:
        has_mean = any("did you mean" in n.lower() for n in diag.notes)
        has_forget = any("did you forget" in n.lower() for n in diag.notes)
        is_linker = "undefined reference" in (diag.message + " " + " ".join(diag.notes)).lower()

        feature_dict = {
            "primary_message": diag.message,
            "primary_notes": " || ".join(diag.notes),
            "primary_hints": " || ".join([n for n in diag.notes if "did you mean" in n.lower() or "did you forget" in n.lower()]),
            "has_did_you_mean": has_mean,
            "has_did_you_forget_include": has_forget,
            "is_linker_error": is_linker,
            "error_line": diag.line or 0,
            "error_column": diag.column or 0,
            "num_errors": total_errors,
            "num_followon": total_followons,
            "has_include_iostream": stdlib_flags["has_include_iostream"],
            "has_include_vector": stdlib_flags["has_include_vector"],
            "has_include_string": stdlib_flags["has_include_string"],
            "has_include_map": stdlib_flags["has_include_map"],
            "has_using_namespace_std": stdlib_flags["has_using_namespace_std"],
            "uses_std_prefix": stdlib_flags["uses_std_prefix"],
            "severity": diag.severity
        }

        # Predict ML Category and calibrated confidence
        prediction = classifier.predict(feature_dict)
        pred_category = prediction["category"]
        confidence = prediction["confidence"]
        abstained = prediction["abstained"]
        model_ver = prediction["model_version"]

        # Generate rule-based educational explanation
        raw_expl = generate_explanation(
            category=pred_category if not abstained else None,
            line=diag.line,
            column=diag.column,
            raw_message=diag.message
        )
        explanation_obj = ExplanationItem(**raw_expl)

        err_rec = ErrorRecord(
            submission_id=submission.id,
            line=diag.line,
            column=diag.column,
            severity=diag.severity,
            raw_message=diag.message,
            category=pred_category if not abstained else "ABSTAINED",
            confidence=confidence,
            is_primary=diag.is_primary,
            abstained=abstained,
            model_version=model_ver
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
            category=pred_category if not abstained else "ABSTAINED",
            confidence=confidence,
            abstained=abstained,
            model_version=model_ver,
            explanation=explanation_obj
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
