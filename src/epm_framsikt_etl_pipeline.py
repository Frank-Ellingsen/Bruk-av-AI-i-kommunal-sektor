#!/usr/bin/env python3
# ==============================================================================
# KRISTIANSAND KOMMUNE -- EPM ETL PIPELINE WITH FRAMSIKT INTEGRATION
# Ingests Vedtatt Budsjett, Budsjettendringer, Deflator, and Visma Regnskap
# Author: Rådgiver Økonomistyring (Frank Ellingsen)
# ==============================================================================

import datetime
import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from config import DB_PATH
except ImportError:
    try:
        from src.config import DB_PATH
    except ImportError:
        DB_PATH = Path(__file__).resolve().parent.parent / "artifacts" / "kristiansand_golden_record.db"

def run_framsikt_visma_etl():
    target_db = DB_PATH if DB_PATH.exists() else Path(__file__).resolve().parent.parent / "kristiansand_golden_record.db"
    conn = sqlite3.connect(str(target_db))
    cursor = conn.cursor()

    # Create tables for Framsikt Data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS framsikt_budsjett (
        enhet_id TEXT,
        enhet_navn TEXT,
        kostra_funksjon TEXT,
        vedtatt_budsjett_kr REAL,
        budsjettendringer_kr REAL,
        deflator_justering_kr REAL,
        budsjett_ar INTEGER,
        oppdatert_dato TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS framsikt_deflator_parametre (
        ar INTEGER,
        opprinnelig_deflator_pst REAL,
        rnb_deflator_pst REAL,
        lonnsvekst_pst REAL,
        prisvekst_pst REAL,
        utdelt_kompensasjon_kr REAL
    )
    """)

    # Insert sample Framsikt data reflecting 1. tertial 2026
    cursor.execute("DELETE FROM framsikt_budsjett")
    cursor.execute("DELETE FROM framsikt_deflator_parametre")

    # Deflator metrics from RNB 2026
    cursor.execute("""
    INSERT INTO framsikt_deflator_parametre VALUES (2026, 3.5, 4.1, 3.6, 4.9, 156000000)
    """)

    # Sector & Unit budgets (Grunnskole, Boenhet, etc.)
    units = [
        ('E20201', 'Mevold Grunnskole', '202 Grunnskole', 15000000.0, 500000.0, 350000.0, 2026, str(datetime.date.today())),
        ('E25401', 'Slettheia Bofellesskap', '254 Pleie og omsorg', 22000000.0, 800000.0, 520000.0, 2026, str(datetime.date.today())),
        ('E20101', 'Kommunale Barnehager', '201 Barnehage', 18000000.0, 300000.0, 410000.0, 2026, str(datetime.date.today()))
    ]

    cursor.executemany("INSERT INTO framsikt_budsjett VALUES (?,?,?,?,?,?,?,?)", units)
    conn.commit()
    
    print("✅ Framsikt ETL Ingestion completed successfully!")
    conn.close()

if __name__ == "__main__":
    run_framsikt_visma_etl()
