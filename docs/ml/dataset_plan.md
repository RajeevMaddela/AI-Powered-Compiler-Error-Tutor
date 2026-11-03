# Dataset Plan: Machine Learning Training & Evaluation Data (M2.1 - M2.3)

## 1. Runtime Compiler & Diagnostic Verification
Before writing dataset generation code, the runtime sandbox execution environment and diagnostic parsing pipeline were inspected to ensure 100% equivalence between the training dataset and production runtime.

### 1.1 Shared Sandbox Command & Flags
The sandbox runner in `backend/app/sandbox/runner.py` executes g++ inside the isolated container (`tutor-sandbox:latest`).

To ensure that missing-return issues are reliably surfaced as hard diagnostics with non-zero exit codes (as confirmed with Option A), `-Werror=return-type` is included in the compile flags:

```python
COMPILER_FLAGS = [
    "g++",
    "-std=c++17",
    "-Wall",
    "-Wextra",
    "-Werror=return-type",
    "-fno-diagnostics-show-caret",
    "-fmessage-length=0",
    "-fdiagnostics-color=never",
    "/workspace/main.cpp",
    "-o",
    "/tmp/a.out"
]
```

- **Linking behavior**: The command outputs to an executable (`-o /tmp/a.out`) without `-c`. It runs both compilation and linking steps, enabling real `UNDEFINED_REFERENCE` linker errors to emerge when functions are declared/called but not defined.
- **Missing return diagnostics**: Non-void helper functions missing a return statement trigger `error: control reaches end of non-void function [-Werror=return-type]`. Functions with `return;` trigger `error: return-statement with no value, in function returning '...'`. Both trigger `exit_code != 0` and are parsed into primary error diagnostics.
- **Caret & formatting**: `-fno-diagnostics-show-caret` is enabled; no caret or source line excerpts are rendered in the compiler stderr.
- **Locale**: Forced to `{"LC_ALL": "C", "LANG": "C"}`, producing standard ASCII single quotes (`'...'`), preventing locale-dependent unicode curly quote discrepancies.

### 1.2 Shared Constant Architecture
To prevent divergence between training data generation and live runtime requests, the compiler flags and sandbox configuration are centralized in a shared constants module (`backend/app/compiler/constants.py` / `ml/config.py`).

---

## 2. The 12 Target Error Categories
The taxonomy strictly adheres to the 12 defined classes:

| # | Enum Key | Stage | Description |
|---|---|---|---|
| 1 | `MISSING_SEMICOLON` | SYNTAX | Statement, declaration, or struct/class missing terminating `;` |
| 2 | `UNDECLARED_IDENTIFIER` | SEMANTIC | Identifier used without declaration or outside scope |
| 3 | `TYPE_MISMATCH` | SEMANTIC | Incompatible type in assignment/initialization/return |
| 4 | `UNMATCHED_BRACES` | SYNTAX | Missing or extra `{` or `}` |
| 5 | `UNMATCHED_PARENTHESES` | SYNTAX | Missing or extra `(` or `)` |
| 6 | `MISSING_RETURN` | SEMANTIC | Non-void function missing return statement or returning void |
| 7 | `INVALID_DECLARATION` | SEMANTIC | Conflicting redeclaration, `void` variable, `auto` without init |
| 8 | `MISSING_HEADER` | SEMANTIC | Used standard library entity without including proper header |
| 9 | `MISSING_NAMESPACE` | SEMANTIC | Standard library entity used without `std::` or `using namespace std;` |
| 10 | `UNDEFINED_REFERENCE` | LINKER | Function declared & called but never defined (linker failure) |
| 11 | `WRONG_ARGUMENTS` | SEMANTIC | Incompatible argument count or type mismatch at call site |
| 12 | `CONST_VIOLATION` | SEMANTIC | Mutating const variable, modifying const parameter, etc. |

---

## 3. Implementation Blueprint

### Step 1: Seed Programs (`ml/seeds/`, M2.1)
- Create ≥ 120 standalone C++17 programs covering introductory through intermediate constructs (loops, conditionals, functions with prototypes, classes/structs, arrays, std::vector, std::string, std::map, etc.).
- Validate every seed program compiles cleanly with 0 errors and 0 warnings using `ml/seeds/validate_seeds.py`.
- Generate `seeds_manifest.json` indexing seeds, topics, namespaces, and features.

### Step 2: Category Mutators (`ml/mutators/`, M2.1)
- Implement deterministic Python mutator classes for each of the 12 categories.
- Mutators operate on code tokens while respecting comments and string literals.
- Ensure unit tests in `ml/tests/test_mutators.py` verify determinism, 1-location mutations, and non-applicability safety.

### Step 3: Sandbox Dataset Builder (`ml/dataset/build_dataset.py`, M2.2)
- Apply mutators to seeds, deduplicate by source hash, compile via Docker sandbox runner, and parse via M1.5 parser.
- Verify primary diagnostic matches mutator intent via loose acceptance rules (`verify_rules.py`).
- Target 350–600 accepted records per category, capped at 6 records per (seed, category).
- Split by `seed_id` into 70% train, 15% val, 15% test.
- Export `dataset.jsonl` (with audit source) and flat privacy-compliant CSVs (without any source lines).

### Step 4: Human-Style Evaluation & Out-of-Scope Sets (`ml/data/`, M2.3)
- Hand-craft ≥ 120 independent broken C++ programs across all 12 categories (`human_test/`).
- Create ~40 out-of-scope broken C++ programs (syntax/semantic bugs outside the 12 categories) for threshold tuning (`out_of_scope/`).
- Compile and serialize into `human_test.jsonl` / `human_test.csv` and `out_of_scope.jsonl` / `out_of_scope.csv`.

### Step 5: Verification, Reporting & Test Suite
- Generate `ml/data/dataset_report.md` with statistics, distributions, message diversity, and leakage checks.
- Run complete test suite covering mutators, splits, privacy/leakage, and schema integrity.
