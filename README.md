# AI Powered Compiler Error Tutor

A modern, privacy-first web application that helps beginner programmers understand real C++ compiler errors through sandboxed compilation, diagnostic parsing, machine learning classification, and plain-English actionable guidance.

---

## Architecture Overview

- **Frontend**: React + Vite, locally bundled Monaco Editor (zero CDN), custom CSS tokens (warm off-white / soft charcoal, dark slate text, muted sage/teal accent).
- **Backend**: Python 3.13, FastAPI, Uvicorn, SQLAlchemy, Pydantic, Argon2, JWT cookies.
- **Sandbox**: Docker container (`tutor-sandbox:latest`, Alpine with `g++` and C++ standard library), non-root user (UID 10001), 256MB RAM limit, 1 CPU, 10s timeout, read-only rootfs, max 5 concurrency slots. Code is compiled and linked, never executed.

---

## One-Command Startup

To start both backend and frontend development servers together:
```cmd
start-dev.bat
```

Or start manually in separate terminals:

### 1. Backend Server
```bash
# Activate virtualenv and start FastAPI on port 8000
backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Server
```bash
cd frontend
npm run dev
```
Open **http://localhost:5173** in your browser.

---

## Running Automated Tests

Run the full automated test suite (parser, auth & multi-tenant isolation, sandbox abuse suite):
```bash
backend\.venv\Scripts\pytest.exe -v
```

Run the end-to-end clean state verification demo:
```bash
backend\.venv\Scripts\python.exe backend/run_clean_demo.py
```

---

## Project Roadmap

See [docs/ROADMAP_MODULES.md](docs/ROADMAP_MODULES.md) for serial-numbered tracking of Module 1, Module 2, and Module 3.
