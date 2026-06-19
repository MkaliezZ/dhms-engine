#!/usr/bin/env python3
"""Local-safe DHMS regression checks."""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "validation/outputs"
OUT.mkdir(parents=True, exist_ok=True)


def run_cmd(name, cmd, real_api=False):
    proc = subprocess.run(cmd, cwd=str(ROOT), shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"name": name, "passed": proc.returncode == 0, "real_api": real_api, "output_snippet": proc.stdout[-1000:]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-deepseek-smoke", action="store_true")
    args = parser.parse_args()
    checks = []
    checks.append(run_cmd("python_parse", "PYTHONPYCACHEPREFIX=/tmp/dhms_engine_pycache python3 -m py_compile $(find . -name '*.py' -not -path './.venv/*')"))
    checks.append(run_cmd("product_mock", "PYTHONPYCACHEPREFIX=/tmp/dhms_engine_pycache python3 cli.py test --input 'Does this agent stay consistent?' --models mock --n 1 --report --output reports/local_regression_product"))
    checks.append(run_cmd("dhms_product_mock", "PYTHONPYCACHEPREFIX=/tmp/dhms_engine_pycache python3 cli.py dhms test --input 'Does this agent stay consistent?' --models mock --n 1 --report --output reports/local_regression_dhms_product"))
    checks.append(run_cmd("provider_conformance", "PYTHONPYCACHEPREFIX=/tmp/dhms_engine_pycache python3 validation/provider_conformance/run_provider_conformance.py"))
    checks.append(run_cmd("suite_mock", "PYTHONPYCACHEPREFIX=/tmp/dhms_engine_pycache python3 cli.py test-suite --suite cases/llm_core --models mock --n 1 --report --output reports/local_regression_suite"))
    checks.append(run_cmd("report_paths", "test -f reports/local_regression_suite/suite_report.json && test -f reports/local_regression_suite/suite_report.md && test -f reports/local_regression_suite/suite_report.html"))
    checks.append(run_cmd("key_leak_scan", "! rg -q 'sk-[A-Za-z0-9]+' reports docs validation product README_PRODUCT.md"))
    if args.include_deepseek_smoke:
        checks.append(run_cmd("deepseek_smoke", "PYTHONPYCACHEPREFIX=/tmp/dhms_engine_pycache python3 validation/provider_smoke/run_provider_smoke.py --provider deepseek --model flash --n 1 --max-real-api-calls 3", real_api=True))
    failed = [c for c in checks if not c["passed"]]
    leak = next((not c["passed"] for c in checks if c["name"] == "key_leak_scan"), False)
    result = {
        "status": "PASS" if not failed else "FAIL",
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "checks": checks,
        "real_api_called": any(c["real_api"] for c in checks),
        "api_key_leak_detected": bool(leak),
        "v2_metrics_overridden": False,
        "recommendation": "Local regression checks passed." if not failed else "Inspect failed checks before release.",
    }
    (OUT / "local_regression_report.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / "local_regression_report.md").write_text(to_md(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks": len(checks), "real_api_called": result["real_api_called"], "report": "validation/outputs/local_regression_report.json"}, indent=2))
    return 0 if result["status"] == "PASS" else 1


def to_md(result):
    lines = ["# DHMS Local Regression Report", "", f"Status: {result['status']}", f"Real API called: {result['real_api_called']}", ""]
    for c in result["checks"]:
        lines.append(f"- {'PASS' if c['passed'] else 'FAIL'}: {c['name']}")
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    raise SystemExit(main())
