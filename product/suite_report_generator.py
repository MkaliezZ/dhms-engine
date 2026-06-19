"""Suite report coordinator."""
from pathlib import Path
from typing import Any
from suite_html_report import write_suite_html
from suite_json_report import write_suite_json
from suite_markdown_report import write_suite_markdown

def generate_suite_reports(report: dict[str, Any], output: str) -> dict[str, str]:
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    paths = {"json": str(out/"suite_report.json"), "markdown": str(out/"suite_report.md"), "html": str(out/"suite_report.html")}
    report["report_paths"] = dict(paths)
    write_suite_markdown(report, out)
    write_suite_html(report, out)
    write_suite_json(report, out)
    return paths
