import os
from pathlib import Path
from backend.app.compiler.constants import (
    COMPILER_FLAGS,
    COMPILER_ENV,
    ErrorCategory,
    CATEGORY_STAGES,
)

BASE_DIR = Path(__file__).resolve().parent
SEEDS_DIR = BASE_DIR / "seeds"
MUTATORS_DIR = BASE_DIR / "mutators"
DATA_DIR = BASE_DIR / "data"
HUMAN_TEST_DIR = DATA_DIR / "human_test"
OUT_OF_SCOPE_DIR = DATA_DIR / "out_of_scope"

DOCKER_IMAGE = "tutor-sandbox:latest"
CONCURRENCY_LIMIT = 5
SANDBOX_TIMEOUT_SECONDS = 10
