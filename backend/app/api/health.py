from fastapi import APIRouter
import docker

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health_check():
    docker_status = "ok"
    try:
        client = docker.from_env()
        client.ping()
    except Exception as e:
        docker_status = f"unavailable: {str(e)}"

    return {
        "status": "healthy" if docker_status == "ok" else "degraded",
        "docker_sandbox": docker_status,
        "database": "ok"
    }
