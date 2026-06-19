"""Helpers for loading DHMS product examples."""

from pathlib import Path
from typing import Optional


def load_text(input_text: Optional[str] = None, input_file: Optional[str] = None) -> str:
    if input_text:
        return input_text
    if input_file:
        return Path(input_file).read_text(encoding="utf-8").strip()
    raise ValueError("Either --input or --input-file is required.")

