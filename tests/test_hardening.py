#!/usr/bin/env python3
from pathlib import Path

from src.config import ARTIFACTS_DIR, DB_PATH, REPORTS_DIR

ROOT = Path(__file__).resolve().parents[1]


def test_generated_outputs_are_separated_from_source_data() -> None:
    assert (ROOT / "data").exists()
    assert ARTIFACTS_DIR.exists()
    assert DB_PATH.parent == ARTIFACTS_DIR
    assert REPORTS_DIR.parent == ARTIFACTS_DIR
    assert (ROOT / ".env.example").exists()
    assert (ROOT / ".devcontainer" / "devcontainer.json").exists()
