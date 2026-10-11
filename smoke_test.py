#!/usr/bin/env python3
"""Minimal smoke test for the Kristiansand EPM golden-record pipeline.

Run with:
    python smoke_test.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from src.config import DB_PATH

ROOT = Path(__file__).resolve().parent


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    print("[INFO] Running smoke test...")

    assert_true(DB_PATH.exists(), f"Expected database at {DB_PATH}, but it was not found.")

    conn = sqlite3.connect(DB_PATH)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Dim_Funksjon', 'Dim_Art', 'Dim_Ansvar', 'Dim_Dato', 'Fact_Regnskap', 'Audit_AI_Actions') ORDER BY name;"
        ).fetchall()
        table_names = {row[0] for row in tables}

        expected = {"Dim_Funksjon", "Dim_Art", "Dim_Ansvar", "Dim_Dato", "Fact_Regnskap", "Audit_AI_Actions"}
        assert_true(expected.issubset(table_names), f"Missing expected tables. Found: {sorted(table_names)}")

        counts = {
            "Dim_Funksjon": conn.execute("SELECT COUNT(*) FROM Dim_Funksjon").fetchone()[0],
            "Dim_Art": conn.execute("SELECT COUNT(*) FROM Dim_Art").fetchone()[0],
            "Dim_Ansvar": conn.execute("SELECT COUNT(*) FROM Dim_Ansvar").fetchone()[0],
            "Dim_Dato": conn.execute("SELECT COUNT(*) FROM Dim_Dato").fetchone()[0],
            "Fact_Regnskap": conn.execute("SELECT COUNT(*) FROM Fact_Regnskap").fetchone()[0],
            "Audit_AI_Actions": conn.execute("SELECT COUNT(*) FROM Audit_AI_Actions").fetchone()[0],
        }

        assert_true(counts["Dim_Funksjon"] >= 1, "Dim_Funksjon should contain at least one row.")
        assert_true(counts["Dim_Art"] >= 1, "Dim_Art should contain at least one row.")
        assert_true(counts["Dim_Ansvar"] >= 1, "Dim_Ansvar should contain at least one row.")
        assert_true(counts["Dim_Dato"] >= 1, "Dim_Dato should contain at least one row.")
        assert_true(counts["Fact_Regnskap"] >= 1250, f"Fact_Regnskap rows should be at least 1250, found {counts['Fact_Regnskap']}.")
        assert_true(counts["Audit_AI_Actions"] >= 1, "Audit_AI_Actions should contain at least one row.")

        view_row = conn.execute("SELECT COUNT(*) FROM V_Avvik_YTD").fetchone()[0]
        assert_true(view_row >= 1, "V_Avvik_YTD should return at least one aggregated row.")

        print("[OK] Smoke test passed.")
        print(f"  Fact_Regnskap rows: {counts['Fact_Regnskap']}")
        print(f"  Audit_AI_Actions rows: {counts['Audit_AI_Actions']}")
        print(f"  V_Avvik_YTD rows: {view_row}")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"[FAIL] Smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
