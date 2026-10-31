# Project Roadmap & Module Specification
## AI Powered Compiler Error Tutor

This document defines the complete scope, serial numbered tasks, and status for all three modules. When checking progress, refer to the module and task serial numbers below.

---

## MODULE 1 (Week 1): Foundation, Authentication and Real Compilation
**Goal**: A signed-in user can write C++, press Analyze, and see REAL compiler errors split into separate cards inside a secured sandbox. No ML yet.

| Serial No. | Task / Topic Name | Description | Status |
|:---:|---|---|:---:|
| **M1.1** | Project Skeleton & Config | Directory tree (`frontend/`, `backend/`, `sandbox/`, `ml/`, `docs/`), `.env.example`, `.gitignore`, root orchestrator configs. | **Completed** |
| **M1.2** | Sandbox Container & Runner | Minimal Alpine `g++` Docker image (`tutor-sandbox:latest`), non-root user (UID 10001), 256MB RAM limit, 1 CPU, 10s timeout, read-only rootfs, dropped capabilities, no-new-privileges, max 5 concurrency slots, 503 error handling. | **Completed** |
| **M1.3** | Database Schema & Models | SQLite schema via SQLAlchemy: `users`, `submissions`, `errors`, `feedback`, `consents`, `model_versions`, `retraining_rounds`. | **Completed** |
| **M1.4** | Authentication & Security Engine | Argon2 password hashing, JWT HttpOnly/SameSite cookie session handling, sliding-window login rate limiting, `/register`, `/login`, `/logout`, `/me`. | **Completed** |
| **M1.5** | Compiler Diagnostic Parser | Splits raw `g++` diagnostic output into line, column, severity, attached notes/hints, and computes Primary vs. Follow-on error classification. | **Completed** |
| **M1.6** | Analyze API (`/api/analyze`) | Validates code, runs Docker sandbox compilation, parses errors, logs submission + errors to DB, returns structured JSON. | **Completed** |
| **M1.7** | History & Multi-Tenant Backend | `GET /api/history`, `GET /api/history/{id}`, `DELETE` endpoints with strict tenant authorization (User A cannot access User B's history). | **Completed** |
| **M1.8** | Design Tokens & App Shell | `tokens.css` with 8px grid, modest 6-8px radius, warm off-white (light) and soft charcoal (dark) palettes, muted sage/teal accent, header navigation, theme toggle. | **Completed** |
| **M1.9** | Authentication UI | Centered sign-up and login cards with inline validations, password strength rules, error alerts, and redirect handling. | **Completed** |
| **M1.10** | Monaco Editor & Diagnostics UI | Bundled Monaco editor (zero CDN), C++ syntax highlighting, consolidated header bar (file name + Reset + Analyze buttons), interactive error cards, line jumping, collapsible raw output drawer. | **Completed** |
| **M1.11** | History UI (`/history`) | Submissions history page allowing browsing past compilation runs, viewing timestamps and error counts, inspecting past code + error cards, and deleting entries. | **Completed** |
| **M1.12** | Test Run 1: Automated Test Suite | Automated test suite: parser unit tests (single, cascading, linker errors), auth multi-tenant isolation tests, and 6 sandbox abuse tests (template recursion, memory bomb, output bomb, size limit, fork bomb, `/etc/shadow` include). | **Completed** |
| **M1.13** | Test Run 2: Clean State & Walkthrough | Clean-state wipe (fresh database, containers), re-running full test suite from zero state, end-to-end demo execution (clean file, broken file, history, abuse file) with evidence and walkthrough report. | **Completed** |

---

## MODULE 2 (Week 2): The Machine-Learning Core and Explanations
**Goal**: Every error card displays a predicted category, calibrated confidence, plain-English explanation, fix guidance, and examples across 12 C++ error categories. Low-confidence predictions abstain gracefully.

| Serial No. | Task / Topic Name | Description | Status |
|:---:|---|---|:---:|
| **M2.1** | Seed Programs & Category Mutators | 100+ small valid C++ programs and deterministic mutation scripts for each of the 12 categories. | **Pending** |
| **M2.2** | Sandbox Dataset Builder | Compiles mutants in sandbox, verifies real compiler outputs match expected category, deduplicates, and splits dataset strictly by seed program. | **Pending** |
| **M2.3** | Human-Style Test Set | Curate independent, hand-crafted broken C++ programs reserved exclusively for evaluation (never used for training). | **Pending** |
| **M2.4** | Diagnostic Sanitizer | Sanitizes compiler messages by replacing user identifiers with `<ID>`, preserving language keywords, symbols, and standard-library flags. | **Pending** |
| **M2.5** | Feature Extractor | TF-IDF (word & char n-grams), keyword/symbol flags, hint flags, standard-library presence flags, severity, and position numbers. | **Pending** |
| **M2.6** | Model Training & Calibration | Train Logistic Regression, Linear SVM, Random Forest with grouped cross-validation; calibrate probabilities (Platt scaling/isotonic) and select confidence threshold. | **Pending** |
| **M2.7** | Model Registry & Rollback | Versioned model artifact storage (`.joblib`), metrics summary, SHA-256 checksum, active model pointer, load-at-startup, and rollback capabilities. | **Pending** |
| **M2.8** | Rule-Based Explanation Engine | Deterministic templates for all 12 categories: What happened, Where, How to fix, and Example (wrong vs. corrected). Fill slots from diagnostic record. | **Pending** |
| **M2.9** | Pipeline Integration | Connect sanitizer, classifier, and explanation engine into `/api/analyze`; update error cards to show category, confidence, fix, and abstain notice. | **Pending** |
| **M2.10** | Privacy & Leakage Automated Tests | Test suite verifying that model input vectors never contain raw source lines or student-invented identifiers. | **Pending** |
| **M2.11** | Module 2 Test Runs & Walkthrough | Automated test runs (Run 1 & clean Run 2), human-style test set confusion matrix report, and walkthrough across all 12 categories. | **Pending** |

---

## MODULE 3 (Week 3): Feedback, Consent, Retraining, Dashboard and Deployment
**Goal**: Complete end-to-end platform with student feedback, privacy-preserving retraining rounds, analytics dashboard, production hardening, and deployment configuration.

| Serial No. | Task / Topic Name | Description | Status |
|:---:|---|---|:---:|
| **M3.1** | User Feedback System | "Helpful" / "Not helpful" rating buttons and category correction dropdown on diagnostic cards, saved to database. | **Pending** |
| **M3.2** | Analytics & Mistakes Dashboard | Dashboard view with chart visualizer: error frequency by category, mistakes over time, submission statistics. | **Pending** |
| **M3.3** | Settings & Account Management | User settings: display account email, model version in use, clear history, and delete account. | **Pending** |
| **M3.4** | Retraining Consent Flow | In-app consent mechanism for scheduled retraining rounds ("May we use your stored error data to improve the tutor?"). Default is NO. Stored with timestamps. | **Pending** |
| **M3.5** | Audited Retraining Pipeline | Offline retraining script combining base dataset with consented user corrections only; validates against frozen human test set; only publishes if superior to active model. | **Pending** |
| **M3.6** | Production Hardening | Rate limiting enforcement, payload size caps, strict CORS, HTTPS cookie security, health endpoints (`/api/health`). | **Pending** |
| **M3.7** | Deployment Configuration | Nginx reverse proxy configuration with HTTPS, systemd / docker-compose service management, and GitHub Actions CI workflow. | **Pending** |
| **M3.8** | Documentation & Runbooks | Production README, architecture notes, API documentation, and deployment guides. | **Pending** |
| **M3.9** | Module 3 Test Runs & Final Demo | Full end-to-end test from clean state, security tests (rate limit, forbidden access, oversize requests), consent tests, and final demo walkthrough. | **Pending** |
