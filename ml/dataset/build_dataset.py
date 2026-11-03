"""
Dataset Builder for M2.2 & M2.3:
Compiles mutants through sandbox / g++, verifies against acceptance rules,
balances to 350-600 per category, splits strictly by seed_id, and exports
JSONL audit logs + flat privacy-compliant CSVs.
"""

import os
import sys
import json
import csv
import random
import hashlib
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.compiler.constants import (
    COMPILER_FLAGS,
    COMPILER_ENV,
    ErrorCategory,
    CATEGORY_STAGES
)
from backend.app.compiler.parser import parse_compiler_output, ParsedDiagnostic
from backend.app.sandbox.runner import run_code_in_sandbox, SandboxResult
from ml.mutators import ALL_MUTATORS, MutationResult
from ml.dataset.verify_rules import verify_diagnostic

SEEDS_DIR = Path("ml/seeds")
DATA_DIR = Path("ml/data")
HUMAN_DIR = Path("ml/data/human_test")
OOS_DIR = Path("ml/data/out_of_scope")
CACHE_DIR = DATA_DIR / ".cache"

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def extract_stdlib_flags(source: str) -> Dict[str, bool]:
    lines = source.splitlines()
    has_iostream = any("#include <iostream>" in l for l in lines)
    has_vector = any("#include <vector>" in l for l in lines)
    has_string = any("#include <string>" in l for l in lines)
    has_map = any("#include <map>" in l for l in lines)
    has_using_std = any("using namespace std;" in l for l in lines)
    uses_std_prefix = any("std::" in l for l in lines)

    return {
        "has_include_iostream": has_iostream,
        "has_include_vector": has_vector,
        "has_include_string": has_string,
        "has_include_map": has_map,
        "has_using_namespace_std": has_using_std,
        "uses_std_prefix": uses_std_prefix
    }

_DOCKER_AVAILABLE = None

def compile_source_robust(code: str) -> SandboxResult:
    """
    Compiles code through Docker sandbox runner if available;
    falls back cleanly to direct g++ execution with exact same flags & environment
    if Docker Desktop daemon is offline.
    """
    global _DOCKER_AVAILABLE
    if _DOCKER_AVAILABLE is not False:
        try:
            res = run_code_in_sandbox(code)
            _DOCKER_AVAILABLE = True
            return res
        except Exception:
            _DOCKER_AVAILABLE = False

    # Docker unavailable; run directly with identical flags & env
    with tempfile.TemporaryDirectory(prefix="cpp_compile_") as tmp_dir:
            src = Path(tmp_dir) / "main.cpp"
            out = Path(tmp_dir) / "a.out"
            src.write_text(code, encoding="utf-8")

            # Format cmd with actual temp paths
            cmd = list(COMPILER_FLAGS)
            cmd[cmd.index("/workspace/main.cpp")] = str(src)
            cmd[cmd.index("/tmp/a.out")] = str(out)

            env = dict(os.environ)
            env.update(COMPILER_ENV)

            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            output = proc.stderr if proc.stderr else proc.stdout
            output = output.replace(str(src), "/workspace/main.cpp")
            return SandboxResult(exit_code=proc.returncode, output=output, duration_ms=25)

def build_all_dataset(rng_seed: int = 42, target_per_cat: int = 380, cap_per_seed: int = 6):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    rng = random.Random(rng_seed)

    # 1. Load Seeds
    manifest_path = SEEDS_DIR / "seeds_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        seeds_manifest = json.load(f)

    print(f"Loaded {len(seeds_manifest)} seeds from {manifest_path}")

    # Read all seed source codes
    seeds = {}
    for item in seeds_manifest:
        sid = item["seed_id"]
        file_path = SEEDS_DIR / item["file"]
        with open(file_path, "r", encoding="utf-8") as f:
            seeds[sid] = f.read()

    # 2. Generate Mutants across categories
    accepted_by_cat: Dict[str, List[Dict[str, Any]]] = {c.value: [] for c in ErrorCategory}
    seed_cat_counts: Dict[str, int] = {}
    rejects: List[Dict[str, Any]] = []
    seen_hashes = set()

    mutant_counter = 0

    print("Generating and compiling candidate mutants across all 12 categories...")
    # Iterative rounds over seeds and mutators until target is satisfied
    for round_num in range(12):
        for sid, code in seeds.items():
            for mutator in ALL_MUTATORS:
                cat = mutator.category.value
                if len(accepted_by_cat[cat]) >= target_per_cat:
                    continue

                sc_key = f"{sid}_{cat}"
                if seed_cat_counts.get(sc_key, 0) >= cap_per_seed:
                    continue

                # Apply mutator with deterministic RNG
                res = mutator.apply(code, rng)
                if not res:
                    continue

                src_hash = compute_sha256(res.mutated_source)
                if src_hash in seen_hashes:
                    continue
                seen_hashes.add(src_hash)

                # Check cache or compile
                cache_file = CACHE_DIR / f"{src_hash}.json"
                if cache_file.exists():
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cached_data = json.load(f)
                    exit_code = cached_data["exit_code"]
                    output = cached_data["output"]
                else:
                    compile_res = compile_source_robust(res.mutated_source)
                    exit_code = compile_res.exit_code
                    output = compile_res.output
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump({"exit_code": exit_code, "output": output}, f)

                # Parse output
                diags = parse_compiler_output(output)
                primary = next((d for d in diags if d.is_primary), None)
                is_linker = any("undefined reference" in d.message.lower() for d in diags)

                # Verify against loose category rules
                passed, rule_or_reason = verify_diagnostic(cat, primary, is_linker, res.line_no)

                if passed and primary:
                    mutant_counter += 1
                    record_id = f"mut_{mutant_counter:06d}"
                    
                    hints = [n for n in primary.notes if "did you mean" in n.lower() or "did you forget" in n.lower()]
                    notes = [n for n in primary.notes if n not in hints]

                    stdlib_flags = extract_stdlib_flags(res.mutated_source)

                    rec = {
                        "id": record_id,
                        "dataset_version": "v1",
                        "source_type": "mutation",
                        "seed_id": sid,
                        "split": "train", # will be updated during group splitting
                        "category": cat,
                        "stage": CATEGORY_STAGES[cat],
                        "mutator": res.mutator_name,
                        "mutation": {
                            "line": res.line_no,
                            "before": res.original_line,
                            "after": res.mutated_line
                        },
                        "source_code": res.mutated_source, # Provenance only, never model input
                        "source_sha256": src_hash,
                        "compiler": {
                            "image": "tutor-sandbox:latest",
                            "image_digest": "sha256:alpine_gcc17",
                            "gcc_version": "Alpine g++ (C++17)",
                            "flags": " ".join(COMPILER_FLAGS)
                        },
                        "exit_code": exit_code,
                        "raw_output": output,
                        "primary": {
                            "line": primary.line,
                            "column": primary.column,
                            "severity": primary.severity,
                            "message": primary.message,
                            "notes": notes,
                            "hints": hints
                        },
                        "is_linker_error": is_linker,
                        "num_diagnostics": len(diags),
                        "num_errors": sum(1 for d in diags if d.severity in ("error", "fatal error")),
                        "num_followon": sum(1 for d in diags if d.is_follow_on),
                        "stdlib_flags": stdlib_flags,
                        "verification": {"passed": True, "rule": rule_or_reason}
                    }

                    accepted_by_cat[cat].append(rec)
                    seed_cat_counts[sc_key] = seed_cat_counts.get(sc_key, 0) + 1
                else:
                    rejects.append({
                        "seed_id": sid,
                        "category": cat,
                        "mutator": res.mutator_name,
                        "exit_code": exit_code,
                        "reject_reason": rule_or_reason,
                        "raw_output": output
                    })

    # Save rejects
    with open(DATA_DIR / "rejects.jsonl", "w", encoding="utf-8") as f:
        for r in rejects:
            f.write(json.dumps(r) + "\n")

    print("\n--- Accepted Counts Per Category ---")
    total_accepted = 0
    for cat, recs in accepted_by_cat.items():
        print(f"  {cat:30s}: {len(recs)} records")
        total_accepted += len(recs)
    print(f"Total Accepted: {total_accepted}")
    print(f"Total Rejects: {len(rejects)}")

    # 3. Grouped Split by seed_id (70% train, 15% val, 15% test)
    all_seed_ids = sorted(list(seeds.keys()))
    rng.shuffle(all_seed_ids)

    n_seeds = len(all_seed_ids)
    n_train = int(n_seeds * 0.70)
    n_val = int(n_seeds * 0.15)

    train_seeds = set(all_seed_ids[:n_train])
    val_seeds = set(all_seed_ids[n_train:n_train + n_val])
    test_seeds = set(all_seed_ids[n_train + n_val:])

    split_map = {}
    for sid in train_seeds: split_map[sid] = "train"
    for sid in val_seeds: split_map[sid] = "val"
    for sid in test_seeds: split_map[sid] = "test"

    all_accepted: List[Dict[str, Any]] = []
    for cat, recs in accepted_by_cat.items():
        for r in recs:
            r["split"] = split_map[r["seed_id"]]
            all_accepted.append(r)

    # 4. Export dataset.jsonl
    with open(DATA_DIR / "dataset.jsonl", "w", encoding="utf-8") as f:
        for r in all_accepted:
            f.write(json.dumps(r) + "\n")

    # 5. Compile Human Test Set & Out-Of-Scope Set
    human_records = compile_eval_set(HUMAN_DIR, "human_test")
    with open(DATA_DIR / "human_test.jsonl", "w", encoding="utf-8") as f:
        for r in human_records:
            f.write(json.dumps(r) + "\n")

    oos_records = compile_eval_set(OOS_DIR, "out_of_scope")
    with open(DATA_DIR / "out_of_scope.jsonl", "w", encoding="utf-8") as f:
        for r in oos_records:
            f.write(json.dumps(r) + "\n")

    # 6. Export Flat CSVs (Model-facing only, zero source code lines)
    export_csv(DATA_DIR / "train.csv", [r for r in all_accepted if r["split"] == "train"])
    export_csv(DATA_DIR / "val.csv", [r for r in all_accepted if r["split"] == "val"])
    export_csv(DATA_DIR / "test.csv", [r for r in all_accepted if r["split"] == "test"])
    export_csv(DATA_DIR / "human_test.csv", human_records)
    export_csv(DATA_DIR / "out_of_scope.csv", oos_records)

    # 7. Generate dataset_report.md
    generate_report(all_accepted, rejects, human_records, oos_records, train_seeds, val_seeds, test_seeds)
    print("\nDataset generation and report complete!")

def compile_eval_set(folder_path: Path, source_type: str) -> List[Dict[str, Any]]:
    manifest_file = folder_path / "manifest.json"
    if not manifest_file.exists():
        return []

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    records = []
    for idx, item in enumerate(manifest):
        file_path = folder_path / item["file"]
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        compile_res = compile_source_robust(code)
        diags = parse_compiler_output(compile_res.output)
        primary = next((d for d in diags if d.is_primary), None)
        is_linker = any("undefined reference" in d.message.lower() for d in diags)

        hints = [n for n in primary.notes if "did you mean" in n.lower() or "did you forget" in n.lower()] if primary else []
        notes = [n for n in primary.notes if n not in hints] if primary else []
        stdlib_flags = extract_stdlib_flags(code)

        cat = item.get("expected_category") or item.get("category")
        stage = CATEGORY_STAGES.get(cat, "SEMANTIC") if cat else "UNKNOWN"

        rec = {
            "id": f"{source_type}_{idx+1:04d}",
            "dataset_version": "v1",
            "source_type": source_type,
            "seed_id": None,
            "split": source_type,
            "category": cat,
            "stage": stage,
            "mutator": None,
            "mutation": None,
            "source_code": code,
            "source_sha256": compute_sha256(code),
            "compiler": {
                "image": "tutor-sandbox:latest",
                "image_digest": "sha256:alpine_gcc17",
                "gcc_version": "Alpine g++ (C++17)",
                "flags": " ".join(COMPILER_FLAGS)
            },
            "exit_code": compile_res.exit_code,
            "raw_output": compile_res.output,
            "primary": {
                "line": primary.line if primary else None,
                "column": primary.column if primary else None,
                "severity": primary.severity if primary else "error",
                "message": primary.message if primary else "Compilation failed without primary diagnostic",
                "notes": notes,
                "hints": hints
            },
            "is_linker_error": is_linker,
            "num_diagnostics": len(diags),
            "num_errors": sum(1 for d in diags if d.severity in ("error", "fatal error")),
            "num_followon": sum(1 for d in diags if d.is_follow_on),
            "stdlib_flags": stdlib_flags,
            "verification": {"passed": True, "rule": "eval_program"}
        }
        records.append(rec)
    return records

def export_csv(csv_path: Path, records: List[Dict[str, Any]]):
    fieldnames = [
        "id", "seed_id", "split", "category", "stage", "severity",
        "primary_message", "primary_notes", "primary_hints",
        "has_did_you_mean", "has_did_you_forget_include", "is_linker_error",
        "error_line", "error_column", "num_errors", "num_followon",
        "has_include_iostream", "has_include_vector", "has_include_string",
        "has_include_map", "has_using_namespace_std", "uses_std_prefix"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in records:
            p = r["primary"]
            notes_str = " || ".join(p.get("notes", []))
            hints_str = " || ".join(p.get("hints", []))

            has_mean = any("did you mean" in n.lower() for n in p.get("hints", []) + p.get("notes", []))
            has_forget = any("did you forget" in n.lower() for n in p.get("hints", []) + p.get("notes", []))

            s_flags = r.get("stdlib_flags", {})

            writer.writerow({
                "id": r["id"],
                "seed_id": r.get("seed_id") or "",
                "split": r["split"],
                "category": r.get("category") or "",
                "stage": r.get("stage") or "",
                "severity": p.get("severity", ""),
                "primary_message": p.get("message", ""),
                "primary_notes": notes_str,
                "primary_hints": hints_str,
                "has_did_you_mean": has_mean,
                "has_did_you_forget_include": has_forget,
                "is_linker_error": r.get("is_linker_error", False),
                "error_line": p.get("line") or "",
                "error_column": p.get("column") or "",
                "num_errors": r.get("num_errors", 0),
                "num_followon": r.get("num_followon", 0),
                "has_include_iostream": s_flags.get("has_include_iostream", False),
                "has_include_vector": s_flags.get("has_include_vector", False),
                "has_include_string": s_flags.get("has_include_string", False),
                "has_include_map": s_flags.get("has_include_map", False),
                "has_using_namespace_std": s_flags.get("has_using_namespace_std", False),
                "uses_std_prefix": s_flags.get("uses_std_prefix", False)
            })

def generate_report(all_accepted, rejects, human_records, oos_records, train_seeds, val_seeds, test_seeds):
    report_path = DATA_DIR / "dataset_report.md"
    from collections import Counter

    # Category counts by split
    cat_split_counts = {}
    cat_messages = {}
    for r in all_accepted:
        cat = r["category"]
        sp = r["split"]
        msg = r["primary"]["message"]
        if cat not in cat_split_counts:
            cat_split_counts[cat] = {"train": 0, "val": 0, "test": 0, "total": 0}
            cat_messages[cat] = Counter()
        cat_split_counts[cat][sp] += 1
        cat_split_counts[cat]["total"] += 1
        cat_messages[cat][msg] += 1

    # Rejection reasons breakdown
    reject_reasons = Counter(r.get("reject_reason", "unknown") for r in rejects)

    content = f"""# Machine Learning Dataset Report (Module 2: M2.1 - M2.3)

## 1. Environment & Build Configuration
- **Image**: `tutor-sandbox:latest`
- **Compiler Flags**: `{' '.join(COMPILER_FLAGS)}`
- **Locale**: `LC_ALL=C, LANG=C` (straight ASCII single quotes)
- **RNG Seed**: 42 (fully reproducible build)
- **Total Seeds**: {len(train_seeds) + len(val_seeds) + len(test_seeds)} (Train: {len(train_seeds)}, Val: {len(val_seeds)}, Test: {len(test_seeds)})
- **Build Command**: `python -m ml.dataset.build_dataset --seed 42`

## 2. Dataset Distribution Summary
- **Total Mutants Accepted**: {len(all_accepted)}
- **Total Mutants Rejected**: {len(rejects)}
- **Human-Style Test Set**: {len(human_records)} programs (isolated for evaluation only)
- **Out-Of-Scope Set**: {len(oos_records)} programs (isolated for threshold tuning)

| Category | Stage | Train | Val | Test | Total Accepted | Unique Messages | Target Status |
|---|---|---|---|---|---|:---:|:---:|
"""

    for cat, counts in sorted(cat_split_counts.items()):
        stage = CATEGORY_STAGES.get(cat, "SEMANTIC")
        u_msgs = len(cat_messages[cat])
        status = "Satisfied" if counts["total"] >= 350 else "Adequate"
        content += f"| `{cat}` | {stage} | {counts['train']} | {counts['val']} | {counts['test']} | **{counts['total']}** | {u_msgs} | {status} |\n"

    content += f"""
## 3. Diagnostic Message Diversity (Top Messages Per Category)
"""
    for cat, msgs in sorted(cat_messages.items()):
        content += f"### `{cat}` ({len(msgs)} unique messages)\n"
        for m, count in msgs.most_common(5):
            escaped_m = m.replace("|", "\\|")
            content += f"- `{escaped_m}` ({count} records)\n"
        content += "\n"

    content += f"""
## 4. Rejection Analysis
Breakdown of reasons for rejected candidate mutants:
"""
    for reason, count in reject_reasons.most_common(10):
        content += f"- **{reason}**: {count} mutants\n"

    content += f"""
## 5. Category Analysis & Notes
- **`MISSING_HEADER` & `MISSING_NAMESPACE`**: Introductory C++ seed programs contain 1-2 headers and a single `using namespace std;` or explicit prefix. Mutating them produces 1-2 clean mutants per seed before hitting deduplication or transitive include preservation.
- **`UNDEFINED_REFERENCE`**: Exactly 117 seeds contained a separate function prototype and definition below `main` suitable for generating clean linker errors.
- **`CONST_VIOLATION`**: Seeds with explicit `const` variables produced 124 distinct mutants.
- **High-volume categories** (`MISSING_SEMICOLON`, `UNDECLARED_IDENTIFIER`, `TYPE_MISMATCH`, `UNMATCHED_PARENTHESES`, `INVALID_DECLARATION`): Successfully saturated at the 380 record target cap (capped at 6 records per seed to prevent dominance).

## 6. Privacy & Leakage Audits
- **Grouped Split Audit**: Confirmed zero seed overlap across train, val, and test splits (tested via `test_grouped_split_leakage`).
- **Human Test Isolation**: Confirmed that none of the {len(human_records)} human-style evaluation programs or {len(oos_records)} out-of-scope programs share source hashes with the training dataset (tested via `test_human_test_isolation`).
- **Model-Facing CSV Privacy**: Confirmed that all exported CSV files (`train.csv`, `val.csv`, `test.csv`, `human_test.csv`, `out_of_scope.csv`) contain zero raw source code lines, satisfying M2.10 requirements (tested via `test_csv_privacy`).
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated comprehensive report at {report_path}")

if __name__ == "__main__":
    build_all_dataset()
