"""Suite JSON report."""
import json
from pathlib import Path
from typing import Any, Mapping

def write_suite_json(report: Mapping[str, Any], output_dir: Path) -> str:
    path = output_dir / "suite_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)
