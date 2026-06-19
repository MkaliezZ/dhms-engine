"""Report coordination for DHMS Product Diagnosis v1.3."""

from pathlib import Path
from typing import Any

from html_report import write_html_report
from json_report import write_json_report
from markdown_report import write_markdown_report


def generate_reports(product_result: dict[str, Any], output_dir: str) -> dict[str, str]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": str(destination / "dhms_product_report.json"),
        "markdown": str(destination / "dhms_product_report.md"),
        "html": str(destination / "dhms_product_report.html"),
    }
    product_result["report_paths"] = dict(paths)
    write_markdown_report(product_result, destination)
    write_html_report(product_result, destination)
    write_json_report(product_result, destination)
    return paths
