"""Entry point for DHMS v2 execution."""

import sys
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = CURRENT_DIR.parent
ROOT_DIR = ENGINE_DIR.parent
PATHS = (
    ENGINE_DIR / "v0",
    ENGINE_DIR / "v1",
    ENGINE_DIR / "cross_model",
    ENGINE_DIR / "statistics",
    ENGINE_DIR / "v2_cross_model",
    ROOT_DIR / "binding",
)
for path in PATHS:
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from v2_orchestrator import run_v2_experiment  # noqa: E402


def run(mode: str, input_text: str, n: int = 1, models: str = "mock") -> dict[str, Any]:
    return run_v2_experiment(mode, input_text, n=n, models=models)

