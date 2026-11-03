from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import docker

from backend.app.core.database import get_db
from ml.pipeline.classifier import get_classifier

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    docker_status = "ok"
    try:
        client = docker.from_env()
        client.ping()
    except Exception as e:
        docker_status = f"unavailable: {str(e)}"

    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    clf = get_classifier()
    model_version = clf.version if clf else "none"

    overall_status = "healthy" if (docker_status == "ok" and db_status == "ok") else "degraded"

    return {
        "status": overall_status,
        "docker_sandbox": docker_status,
        "database": db_status,
        "active_model_version": model_version
    }
