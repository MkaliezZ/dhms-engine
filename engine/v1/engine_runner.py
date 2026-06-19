"""Entry point for DHMS engine execution."""

import sys
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = CURRENT_DIR.parent
ROOT_DIR = ENGINE_DIR.parent
PATHS = (CURRENT_DIR, ENGINE_DIR / "v0", ROOT_DIR / "binding")
for path in PATHS:
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from experiment_orchestrator import run_experiment  # noqa: E402


def run(mode: str, input_text: str, n: int = 1) -> dict[str, Any]:
    return run_experiment(mode, input_text, n=n)
