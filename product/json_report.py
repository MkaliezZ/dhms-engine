"""JSON report writer for DHMS Product Diagnosis v1.3."""

import json
from pathlib import Path
from typing import Any, Mapping


def write_json_report(product_result: Mapping[str, Any], output_dir: Path) -> str:
    path = output_dir / "dhms_product_report.json"
    path.write_text(json.dumps(product_result, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)

