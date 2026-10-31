import os
import time
import tempfile
import threading
from typing import Tuple, Dict, Any
from fastapi import HTTPException, status
import docker
from docker.errors import DockerException, APIError
from backend.app.core.config import settings

# Concurrency semaphore: max concurrent sandboxes
_sandbox_semaphore = threading.BoundedSemaphore(settings.SANDBOX_MAX_CONCURRENT)

class SandboxResult:
    def __init__(self, exit_code: int, output: str, duration_ms: int, timed_out: bool = False):
        self.exit_code = exit_code
        self.output = output
        self.duration_ms = duration_ms
        self.timed_out = timed_out

    @property
    def is_clean(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


def run_code_in_sandbox(code: str) -> SandboxResult:
    """
    Executes C++ compilation inside an isolated Docker sandbox container with strict limits.
    Never executes the compiled code.
    """
    # Enforce input code size cap
    code_bytes = code.encode("utf-8")
    if len(code_bytes) > settings.SANDBOX_MAX_CODE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Source code exceeds maximum allowed size of {settings.SANDBOX_MAX_CODE_BYTES // 1024} KB."
        )

    # Acquire concurrency slot (wait up to 2 seconds before answering server busy)
    acquired = _sandbox_semaphore.acquire(timeout=2.0)
    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is busy. All compilation workers are currently occupied. Please try again shortly."
        )

    try:
        try:
            client = docker.from_env()
            client.ping()
        except DockerException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Sandbox service unavailable: Docker daemon is not accessible ({str(e)})."
            )

        start_time = time.time()
        timed_out = False
        output = ""
        exit_code = -1

        # Create isolated temp folder with random name on host
        with tempfile.TemporaryDirectory(prefix="cpp_sandbox_") as temp_dir:
            source_file = os.path.join(temp_dir, "main.cpp")
            with open(source_file, "wb") as f:
                f.write(code_bytes)

            container = None
            try:
                container = client.containers.create(
                    image=settings.DOCKER_SANDBOX_IMAGE,
                    command=[
                        "g++",
                        "-std=c++17",
                        "-Wall",
                        "-Wextra",
                        "-fno-diagnostics-show-caret",
                        "-fmessage-length=0",
                        "-fdiagnostics-color=never",
                        "/workspace/main.cpp",
                        "-o",
                        "/tmp/a.out"
                    ],
                    network_mode="none",
                    mem_limit="256m",
                    memswap_limit="256m",
                    nano_cpus=1000000000,
                    pids_limit=64,
                    read_only=True,
                    tmpfs={
                        "/tmp": "rw,noexec,nosuid,size=64m"
                    },
                    volumes={
                        temp_dir: {"bind": "/workspace", "mode": "ro"}
                    },
                    user="10001",
                    cap_drop=["ALL"],
                    security_opt=["no-new-privileges:true"],
                    environment={"LC_ALL": "C", "LANG": "C"}
                )

                container.start()

                # Wait for container with strict timeout
                try:
                    result = container.wait(timeout=settings.SANDBOX_TIMEOUT_SECONDS)
                    exit_code = result.get("StatusCode", -1)
                except Exception:  # Timeout exception from docker-py
                    timed_out = True
                    try:
                        container.kill()
                    except Exception:
                        pass
                    exit_code = 124  # Standard timeout exit code

                # Fetch logs capped at output limit
                raw_logs = container.logs(stdout=True, stderr=True)
                if len(raw_logs) > settings.SANDBOX_MAX_OUTPUT_BYTES:
                    raw_logs = raw_logs[:settings.SANDBOX_MAX_OUTPUT_BYTES] + b"\n... [Compiler output truncated: limit exceeded]"
                output = raw_logs.decode("utf-8", errors="replace")

            finally:
                if container:
                    try:
                        container.remove(force=True)
                    except Exception:
                        pass

        duration_ms = int((time.time() - start_time) * 1000)

        if timed_out:
            output = f"Compilation timed out after {settings.SANDBOX_TIMEOUT_SECONDS} seconds.\n" + output

        return SandboxResult(
            exit_code=exit_code,
            output=output,
            duration_ms=duration_ms,
            timed_out=timed_out
        )

    finally:
        _sandbox_semaphore.release()
