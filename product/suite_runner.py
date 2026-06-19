"""Suite runner for DHMS Product Layer."""
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from product_runner import run_product_test
from suite_report_generator import generate_suite_reports
from suite_summary import summarize_suite


def run_suite(*, suite: str, models: str = "mock", n: int = 1, mode: str = "B", report: bool = False, output: str = "reports/latest_suite") -> dict[str, Any]:
    suite_path = Path(suite)
    cases = sorted(suite_path.rglob("*.txt"))
    per_case = []
    per_case_dir = Path(output) / "per_case"
    suite_run_id = build_suite_run_id(suite_path, models, n)
    for case_path in cases:
        case_id = str(case_path.relative_to(suite_path)).replace("/", "__").replace(".txt", "")
        case_output = per_case_dir / slug(case_id)
        metadata = {
            "case_id": case_id,
            "case_path": str(case_path),
            "case_category": case_category(suite_path, case_path),
            "suite_name": str(suite_path),
            "suite_run_id": suite_run_id,
            "suite_output_dir": output,
        }
        result = run_product_test(input_file=str(case_path), models=models, n=n, mode=mode, report=report, output=str(case_output), case_metadata=metadata)
        per_case.append(result)
    summary = summarize_suite(str(suite_path), per_case, models, n)
    suite_report = {"suite_name": str(suite_path), "suite_run_id": suite_run_id, "summary": summary, "case_results": per_case, "report_paths": {}}
    if report:
        suite_report["report_paths"] = generate_suite_reports(suite_report, output)
    return suite_report


def slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value)


def build_suite_run_id(suite_path: Path, models: str, n: int) -> str:
    suite_label = slug(suite_path.name or "suite")
    model_label = slug(models.replace(",", "_").replace(":", "_"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{suite_label}__{model_label}__n{n}__{timestamp}"


def case_category(suite_path: Path, case_path: Path) -> str:
    relative = case_path.relative_to(suite_path)
    return relative.parts[0] if len(relative.parts) > 1 else "not_available"
