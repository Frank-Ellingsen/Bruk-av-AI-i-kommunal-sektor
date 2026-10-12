#!/usr/bin/env python3
"""Minimal smoke tests for the EPM pipeline."""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

from src.config import DB_PATH

ROOT = Path(__file__).resolve().parents[1]


def test_gold_record_builds() -> None:
    subprocess.run([sys.executable, "src/build_golden_record.py"], cwd=str(ROOT), check=True)
    subprocess.run([sys.executable, "src/build_golden_record.py", "--keep-existing"], cwd=str(ROOT), check=True)

    assert DB_PATH.exists(), f"Expected database at {DB_PATH}"

    conn = sqlite3.connect(DB_PATH)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Dim_Funksjon', 'Dim_Art', 'Dim_Ansvar', 'Dim_Dato', 'Fact_Regnskap', 'Audit_AI_Actions') ORDER BY name;"
        ).fetchall()
        table_names = {row[0] for row in tables}

        expected = {"Dim_Funksjon", "Dim_Art", "Dim_Ansvar", "Dim_Dato", "Fact_Regnskap", "Audit_AI_Actions"}
        assert expected.issubset(table_names), f"Missing expected tables: {sorted(table_names)}"

        assert conn.execute("SELECT COUNT(*) FROM Fact_Regnskap").fetchone()[0] >= 1250
        assert conn.execute("SELECT COUNT(*) FROM Audit_AI_Actions").fetchone()[0] >= 1
        assert conn.execute("SELECT COUNT(*) FROM V_Avvik_YTD").fetchone()[0] >= 1
    finally:
        conn.close()
