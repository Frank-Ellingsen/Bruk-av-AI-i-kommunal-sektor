#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if value:
        return Path(value).expanduser().resolve()
    return default


ARTIFACTS_DIR = _env_path("KRISTIANSAND_ARTIFACTS_DIR", PROJECT_ROOT / "artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = _env_path("KRISTIANSAND_DB_PATH", ARTIFACTS_DIR / "kristiansand_golden_record.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATA_DIR = _env_path("KRISTIANSAND_DATA_DIR", PROJECT_ROOT / "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

REPORTS_DIR = _env_path("KRISTIANSAND_REPORTS_DIR", ARTIFACTS_DIR / "reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
