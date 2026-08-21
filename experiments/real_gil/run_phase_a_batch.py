from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "experiments" / "real_gil" / "run_real_gil_experiment.py"
OUT = ROOT / "artifacts" / "real-gil" / "phase-a-summary.json"


def run_case(module: str, expect_reactivation: bool, runs: int) -> list[dict]:
    rows = []
    for i in range(1, runs + 1):
        cmd = [sys.executable, str(RUNNER), module]
        if expect_reactivation:
            cmd.append("--expect-reactivation")
        env = {**os.environ}
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, env=env)
        payload = json.loads(result.stdout)
        payload["batch_run"] = i
        payload["process_returncode"] = result.returncode
        rows.append(payload)
        # Any real-runtime unexpected result is a hard failure.  ENVIRONMENT_NOT_READY
        # is handled by the caller when a suitable runtime is absent.
        if payload["status"] == "ENVIRONMENT_NOT_READY":
            break
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()

    control = run_case("compatible_ext", False, args.runs)
    treatment = run_case("incompatible_ext", True, args.runs)

    all_rows = control + treatment
    env_ready = all(r["status"] != "ENVIRONMENT_NOT_READY" for r in all_rows)

    def control_pass(rows: list[dict]) -> bool:
        return bool(rows) and len(rows) == args.runs and all(
            r["status"] == "PASS" and r["causal_attribution"] is False and
            r["runtime_before"]["gil_enabled"] is False and
            r["runtime_after"]["gil_enabled"] is False and
            r["temporal_order_ok"] is True for r in rows
        )

    def treatment_pass(rows: list[dict]) -> bool:
        return bool(rows) and len(rows) == args.runs and all(
            r["status"] == "PASS" and r["causal_attribution"] is True and
            r["failure_code"] == "UNEXPECTED_GIL_REACTIVATION" and
            r["runtime_before"]["gil_enabled"] is False and
            r["runtime_after"]["gil_enabled"] is True and
            r["temporal_order_ok"] is True for r in rows
        )

    accepted = env_ready and control_pass(control) and treatment_pass(treatment)
    summary = {
        "experiment": "PHASE_A_REAL_GIL_BATCH",
        "runs_per_condition": args.runs,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "environment_ready": env_ready,
        "control_pass": control_pass(control),
        "treatment_pass": treatment_pass(treatment),
        "accepted": accepted,
        "causal_detection_rate": (
            sum(1 for r in treatment if r.get("failure_code") == "UNEXPECTED_GIL_REACTIVATION") / len(treatment)
            if treatment else 0.0
        ),
        "causal_attribution_accuracy": (
            sum(1 for r in treatment if r.get("causal_attribution") is True) / len(treatment)
            if treatment else 0.0
        ),
        "control_pass_rate": (
            sum(1 for r in control if r.get("status") == "PASS" and r.get("runtime_after", {}).get("gil_enabled") is False) / len(control)
            if control else 0.0
        ),
        "evidence_chain_completeness": (
            sum(1 for r in all_rows if bool(r.get("events")) and bool(r.get("module")) and bool(r.get("runtime_before")) and bool(r.get("runtime_after"))) / len(all_rows)
            if all_rows else 0.0
        ),
        "control_runs": control,
        "treatment_runs": treatment,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps({k: summary[k] for k in ("environment_ready", "control_pass", "treatment_pass", "accepted", "causal_detection_rate", "causal_attribution_accuracy", "control_pass_rate", "evidence_chain_completeness")}, indent=2))
    return 0 if accepted or not env_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
