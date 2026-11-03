import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.dataset.build_dataset import compile_source_robust
from backend.app.compiler.parser import parse_compiler_output

SEEDS_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = SEEDS_DIR / "seeds_manifest.json"

def validate_all_seeds():
    if not MANIFEST_PATH.exists():
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)
        
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    print(f"Validating {len(manifest)} seed programs with runtime sandbox flags...")
    passed = 0
    failed = []
    
    for item in manifest:
        seed_id = item["seed_id"]
        file_path = SEEDS_DIR / item["file"]
        
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            
        res = compile_source_robust(code)
        diagnostics = parse_compiler_output(res.output)
        
        # Must compile with exit_code == 0, not timed out, and 0 errors/warnings
        if res.exit_code == 0 and not res.timed_out and len(diagnostics) == 0:
            passed += 1
        else:
            errors_summary = [f"{d.severity}: {d.message} (L{d.line})" for d in diagnostics]
            failed.append({
                "seed_id": seed_id,
                "exit_code": res.exit_code,
                "timed_out": res.timed_out,
                "diagnostics": errors_summary,
                "raw_output": res.output
            })
            print(f"  FAILED: {seed_id} (exit={res.exit_code}, diag_count={len(diagnostics)})")
            for diag in diagnostics:
                print(f"     -> [{diag.severity}] Line {diag.line}: {diag.message}")
                
    print(f"\nValidation Summary: {passed}/{len(manifest)} seeds PASSED cleanly (0 errors, 0 warnings).")
    
    if failed:
        print(f"FAILED SEEDS: {len(failed)}")
        return False
    return True

if __name__ == "__main__":
    success = validate_all_seeds()
    sys.exit(0 if success else 1)
