# System Architecture & Technical Specification

## 1. Overview
The **AI Powered Compiler Error Tutor** is an interactive educational tool designed to assist computer science students when learning C++. It combines sandboxed compilation with machine-learning error classification and pedagogical explanations across 12 distinct C++ error categories.

```
+-----------------------------------------------------------+
|                   React + Monaco Frontend                 |
|   (Code Editor, Diagnostic Cards, Feedback, Dashboard)    |
+-----------------------------+-----------------------------+
                              | HTTP (JSON / Cookies)
+-----------------------------v-----------------------------+
|                     FastAPI Backend                       |
|   - Multi-tenant auth & JWT HttpOnly session handling     |
|   - Rate limiters & 64 KB payload security filters        |
|   - Production Security Headers Middleware                |
+--------------+-----------------------------+--------------+
               |                             |
+--------------v---------------+  +----------v--------------+
| Docker g++ Sandbox Runner    |  | SQLite Database Engine   |
| (10s timeout, cgroups limits)|  | (Users, Errors, Feedbacks|
| -std=c++17 -Wall -Wextra     |  | Consents, Model Registry)|
+--------------+---------------+  +-------------------------+
               |
+--------------v---------------+
| Diagnostic Parser & AST      |
| Normalizer                   |
+--------------+---------------+
               |
+--------------v---------------+
| Privacy Sanitizer (<ID>)     |
+--------------+---------------+
               |
+--------------v---------------+
| ML Error Classifier & Calib. |
| (Logistic Regression Bundle) |
+--------------+---------------+
               |
+--------------v---------------+
| Pedagogical Explanation      |
| Engine (Fix Checklist & Diffs|
+------------------------------+
```

## 2. Core Subsystems

### A. Compiler Sandbox Runner (Module 1)
- Isolated g++ runner using Docker or local host fallback.
- Standard flags: `-std=c++17 -Wall -Wextra -Werror=return-type -fno-diagnostics-show-caret -fmessage-length=0 -fdiagnostics-color=never`.
- Timeout: 10 seconds. Limits CPU and memory.

### B. Machine Learning Core (Module 2)
- **12 Target Error Categories**:
  1. `MISSING_SEMICOLON`
  2. `UNDECLARED_IDENTIFIER`
  3. `TYPE_MISMATCH`
  4. `UNMATCHED_BRACES`
  5. `UNMATCHED_PARENTHESES`
  6. `MISSING_RETURN`
  7. `INVALID_DECLARATION`
  8. `MISSING_HEADER`
  9. `MISSING_NAMESPACE`
  10. `UNDEFINED_REFERENCE`
  11. `WRONG_ARGUMENTS`
  12. `CONST_VIOLATION`
- **Privacy First**: `DiagnosticSanitizer` replaces student variables/function names with `<ID>`, preserving C++ language tokens.
- **Calibrated Abstention**: Predictions below confidence threshold `0.55` abstain safely rather than guessing.

### C. Feedback, Retraining & Analytics (Module 3)
- **Feedback**: Users rate explanations (helpful / not helpful) and propose corrected categories.
- **Consent Flow**: By default, user consent is `denied`. Opt-in enables anonymized diagnostic retraining.
- **Audited Retraining**: Candidate models must match or exceed the frozen human benchmark accuracy before automated deployment.

