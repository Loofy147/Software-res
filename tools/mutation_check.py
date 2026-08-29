"""Simple mutation harness for the non-compensatory decision policy."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src/resilience_poc/models.py"
SRC_ROOT = ROOT / "src"

MUTANTS = {
    "unknown_to_pass": ('elif status in {"warn", "unknown"}:', 'elif status in {"warn"}:', ["test_any_critical_unknown_cannot_auto_merge"]),
    "fail_condition_removed": ('if status == "fail":', 'if False:', ["test_any_critical_fail_rejects"]),
    "risk_gate_removed": ('if risk_tier != "low":', 'if False:', ["test_non_low_risk_never_auto_merges"]),
}


def main():
    original = SRC.read_text()
    failures = []
    for name, (needle, replacement, expected_tests) in MUTANTS.items():
        if needle not in original:
            failures.append((name, "mutation target not found"))
            continue
        with tempfile.TemporaryDirectory():
            backup = SRC.with_suffix('.bak')
            try:
                shutil.copy2(SRC, backup)
                SRC.write_text(original.replace(needle, replacement, 1))
                cmd = [sys.executable, "-m", "pytest", "-q", "tests/test_policy_invariants_v2.py"]
                env = os.environ.copy()
                # Mutation testing must execute the mutated working-tree source, not a
                # previously installed immutable wheel from the calling environment.
                env["PYTHONPATH"] = f"{SRC_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
                result = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
                # A good mutation test expects the suite to FAIL on the mutant.
                if result.returncode == 0:
                    failures.append((name, "mutation survived"))
                print(name, "KILLED" if result.returncode != 0 else "SURVIVED")
            finally:
                if backup.exists():
                    shutil.move(backup, SRC)
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
