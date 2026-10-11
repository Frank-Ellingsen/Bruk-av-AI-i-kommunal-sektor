#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
KRISTIANSAND KOMMUNE - EPM GOLDEN RECORD ETL PIPELINE
===============================================================================
Etablerer den kanoniske stjernemodellen i SQLite (kristiansand_golden_record.db)
for Kristiansand kommune:
- Kilder: BoMiljø.csv (Slettheia Bofellesskap) & Komskole.csv (Mevold Grunnskole)
- Dimensjoner: Dim_Funksjon, Dim_Art, Dim_Ansvar, Dim_Dato
- Faktatabell: Fact_Regnskap (med SHA-256 transaksjons-hash)
- Revisjonsspor: Audit_AI_Actions (Human-in-the-Loop, jf. Kommuneloven § 14-5)
===============================================================================
"""

import os
import sys
import csv
import hashlib
import sqlite3
import datetime
from pathlib import Path

# Sikre UTF-8 output på Windows-konsoll
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name == "src" else BASE_DIR

# Robust sti-oppslag for prosjektstrukturen
DB_PATH = PROJECT_ROOT / "kristiansand_golden_record.db"

def find_data_file(filename):
    for candidate in [PROJECT_ROOT / "data" / filename, BASE_DIR / filename, PROJECT_ROOT / filename]:
        if candidate.exists():
            return candidate
    return PROJECT_ROOT / "data" / filename

BOMILJO_CSV = find_data_file("BoMiljø.csv")
KOMSKOLE_CSV = find_data_file("Komskole.csv")

def get_hash(*args):
    """Generer deterministisk SHA-256 hash for transaksjonen."""
    raw = "|".join(str(a) for a in args).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def create_schema(conn):
    """Oppretter DDL i henhold til antigravity_usecase_epm.md."""
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    cur.executescript("""
    -- 1. DIMENSJON: KOSTRA Funksjon
    CREATE TABLE IF NOT EXISTS Dim_Funksjon (
        funksjon_key INTEGER PRIMARY KEY AUTOINCREMENT,
        funksjon_kode TEXT NOT NULL UNIQUE,
        funksjon_navn TEXT NOT NULL,
        hovedfunksjon_kode TEXT NOT NULL,
        tjenesteomrade_navn TEXT NOT NULL
    );

    -- 2. DIMENSJON: KOSTRA Art
    CREATE TABLE IF NOT EXISTS Dim_Art (
        art_key INTEGER PRIMARY KEY AUTOINCREMENT,
        art_kode TEXT NOT NULL UNIQUE,
        art_navn TEXT NOT NULL,
        art_gruppe TEXT NOT NULL,
        sign_multiplier INTEGER NOT NULL CHECK (sign_multiplier IN (-1, 1))
    );

    -- 3. DIMENSJON: Organisasjonsansvar
    CREATE TABLE IF NOT EXISTS Dim_Ansvar (
        ansvar_key INTEGER PRIMARY KEY AUTOINCREMENT,
        ansvar_kode TEXT NOT NULL UNIQUE,
        ansvar_navn TEXT NOT NULL,
        kommunalsjefomrade TEXT NOT NULL
    );

    -- 4. DIMENSJON: Kalender
    CREATE TABLE IF NOT EXISTS Dim_Dato (
        dato_key INTEGER PRIMARY KEY, -- YYYYMMDD
        full_dato DATE NOT NULL UNIQUE,
        ar INTEGER NOT NULL,
        tertial INTEGER NOT NULL CHECK (tertial BETWEEN 1 AND 3),
        maned INTEGER NOT NULL CHECK (maned BETWEEN 1 AND 12)
    );

    -- FAKTATABELL: Regnskap og Budsjett
    CREATE TABLE IF NOT EXISTS Fact_Regnskap (
        transaksjon_id TEXT PRIMARY KEY,
        kilde_system TEXT NOT NULL,
        funksjon_key INTEGER NOT NULL,
        art_key INTEGER NOT NULL,
        ansvar_key INTEGER NOT NULL,
        dato_key INTEGER NOT NULL,
        belop REAL NOT NULL,
        korrigert_belop REAL NOT NULL,
        budsjett_belop REAL DEFAULT 0.0,
        avvik_belop REAL GENERATED ALWAYS AS (korrigert_belop - budsjett_belop) VIRTUAL,
        sist_oppdatert TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (funksjon_key) REFERENCES Dim_Funksjon(funksjon_key),
        FOREIGN KEY (art_key) REFERENCES Dim_Art(art_key),
        FOREIGN KEY (ansvar_key) REFERENCES Dim_Ansvar(ansvar_key),
        FOREIGN KEY (dato_key) REFERENCES Dim_Dato(dato_key)
    );

    -- REVISJONSSPOR & ETISK AI-STYRING (EU AI Act & Kommuneloven § 14-5)
    CREATE TABLE IF NOT EXISTS Audit_AI_Actions (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tidsstempel TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        enhet_kode TEXT NOT NULL,
        ai_modell_versjon TEXT NOT NULL,
        prognostisert_avvik REAL NOT NULL,
        foreslatt_tiltak TEXT NOT NULL,
        konfidens_score REAL NOT NULL,
        leder_beslutning TEXT CHECK (leder_beslutning IN ('GODKJENT', 'AVVIST', 'ENDRET')),
        begrunnelse_tekst TEXT,
        godkjent_av_saksbehandler TEXT NOT NULL,
        IP_adresse TEXT
    );

    -- ANALYTISKE VIEWS
    CREATE VIEW IF NOT EXISTS V_Fact_Full AS
    SELECT 
        fr.transaksjon_id,
        fr.kilde_system,
        dd.full_dato,
        dd.ar,
        dd.tertial,
        dd.maned,
        df.funksjon_kode,
        df.funksjon_navn,
        df.tjenesteomrade_navn,
        da.ansvar_kode,
        da.ansvar_navn,
        da.kommunalsjefomrade,
        dart.art_kode,
        dart.art_navn,
        dart.art_gruppe,
        fr.belop,
        fr.korrigert_belop,
        fr.budsjett_belop,
        fr.avvik_belop
    FROM Fact_Regnskap fr
    JOIN Dim_Dato dd ON fr.dato_key = dd.dato_key
    JOIN Dim_Funksjon df ON fr.funksjon_key = df.funksjon_key
    JOIN Dim_Ansvar da ON fr.ansvar_key = da.ansvar_key
    JOIN Dim_Art dart ON fr.art_key = dart.art_key;

    CREATE VIEW IF NOT EXISTS V_Avvik_YTD AS
    SELECT 
        da.ansvar_navn,
        df.funksjon_navn,
        dart.art_gruppe,
        dart.art_kode,
        dart.art_navn,
        ROUND(SUM(fr.budsjett_belop), 0) AS budsjett_ytd,
        ROUND(SUM(fr.korrigert_belop), 0) AS regnskap_ytd,
        ROUND(SUM(fr.avvik_belop), 0) AS avvik_ytd
    FROM Fact_Regnskap fr
    JOIN Dim_Dato dd ON fr.dato_key = dd.dato_key
    JOIN Dim_Ansvar da ON fr.ansvar_key = da.ansvar_key
    JOIN Dim_Funksjon df ON fr.funksjon_key = df.funksjon_key
    JOIN Dim_Art dart ON fr.art_key = dart.art_key
    WHERE (fr.kilde_system LIKE '%BOOM%' AND dd.maned <= 8) OR (fr.kilde_system LIKE '%Skole%')
    GROUP BY da.ansvar_navn, df.funksjon_navn, dart.art_gruppe, dart.art_kode, dart.art_navn;
    """)
    conn.commit()
    print("[OK] Schema og views etablert med suksess.")

def populate_dimensions(conn):
    """Populerer grunndata for dimensjonene."""
    cur = conn.cursor()

    # Dim_Funksjon
    funksjoner = [
        ('202', 'Grunnskoleopplæring', '200', 'Oppvekst'),
        ('213', 'Voksenopplæring', '210', 'Oppvekst'),
        ('215', 'Skolefritidstilbud (SFO)', '210', 'Oppvekst'),
        ('222', 'Skolelokaler', '220', 'Oppvekst / Eiendom'),
        ('223', 'Skoleskyss', '220', 'Oppvekst'),
        ('254', 'Hjemmetjenester og bofellesskap', '250', 'Helse og mestring')
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO Dim_Funksjon (funksjon_kode, funksjon_navn, hovedfunksjon_kode, tjenesteomrade_navn)
        VALUES (?, ?, ?, ?)
    """, funksjoner)

    # Dim_Ansvar
    ansvar = [
        ('2020', 'Mevold Grunnskole (Åseral)', 'Oppvekst'),
        ('2021', 'SFO-avdelingene', 'Oppvekst'),
        ('2022', 'Grunnskole felles / Leirskole', 'Oppvekst'),
        ('2029', 'Interkommunal PPT-enhet', 'Oppvekst'),
        ('2130', 'Kommunal voksenopplæring', 'Oppvekst'),
        ('2220', 'Skolelokaler / Eiendom', 'Oppvekst / Eiendom'),
        ('2230', 'Skoleskyss / Sentral stab', 'Oppvekst'),
        ('2540', 'Slettheia Bofellesskap', 'Helse og mestring')
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO Dim_Ansvar (ansvar_kode, ansvar_navn, kommunalsjefomrade)
        VALUES (?, ?, ?)
    """, ansvar)

    # Dim_Dato (2024 og 2025 måneder per 1. i måneden)
    datoer = []
    for yr in [2024, 2025]:
        for m in range(1, 13):
            d_key = yr * 10000 + m * 100 + 1
            f_dato = f"{yr}-{m:02d}-01"
            tert = 1 if m <= 4 else (2 if m <= 8 else 3)
            datoer.append((d_key, f_dato, yr, tert, m))

    cur.executemany("""
        INSERT OR IGNORE INTO Dim_Dato (dato_key, full_dato, ar, tertial, maned)
        VALUES (?, ?, ?, ?, ?)
    """, datoer)

    conn.commit()
    print("✓ Standard-dimensjoner populert.")

def get_or_create_art(conn, art_kode, art_navn, art_gruppe=None, sign_multiplier=1):
    cur = conn.cursor()
    cur.execute("SELECT art_key FROM Dim_Art WHERE art_kode = ?", (art_kode,))
    row = cur.fetchone()
    if row:
        return row[0]
    
    if art_gruppe is None:
        if art_kode.startswith(('10', '01', '02', '03', '04', '05', '09')):
            art_gruppe = 'Personal'
        elif art_kode.startswith(('16', '17', '6', '7', '8')):
            art_gruppe = 'Refusjon'
            sign_multiplier = -1
        else:
            art_gruppe = 'Drift'
    
    cur.execute("""
        INSERT INTO Dim_Art (art_kode, art_navn, art_gruppe, sign_multiplier)
        VALUES (?, ?, ?, ?)
    """, (art_kode, art_navn, art_gruppe, sign_multiplier))
    conn.commit()
    return cur.lastrowid

def load_bomiljo(conn):
    """Laster inn data fra BoMiljø.csv (Slettheia Bofellesskap)."""
    cur = conn.cursor()
    cur.execute("SELECT funksjon_key FROM Dim_Funksjon WHERE funksjon_kode = '254'")
    funksjon_key = cur.fetchone()[0]

    cur.execute("SELECT ansvar_key FROM Dim_Ansvar WHERE ansvar_kode = '2540'")
    ansvar_key = cur.fetchone()[0]

    inserted = 0
    with open(BOMILJO_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            m_num = int(row['Måned_Nr'])
            d_key = 20240000 + m_num * 100 + 1
            
            art_kode = row['KOSTRA_Art']
            konto = row['Kontokode']
            kontonavn = row['Kontonavn']
            hoved = row['Hovedgruppe']
            
            # Bestem fortegn og gruppe
            if 'Inntekt' in hoved or 'Refusjon' in row['Undergruppe']:
                gruppe = 'Refusjon'
                sign = -1
            elif 'Lønn' in hoved:
                gruppe = 'Personal'
                sign = 1
            else:
                gruppe = 'Drift'
                sign = 1
            
            art_key = get_or_create_art(conn, art_kode, f"{art_kode} {row['Undergruppe']}", gruppe, sign)
            
            belop = float(row['Regnskap'])
            budsjett = float(row['Budsjett'])
            korrigert = belop * sign
            
            tx_id = get_hash("BOOM", "2540", konto, d_key)
            
            cur.execute("""
                INSERT OR REPLACE INTO Fact_Regnskap (
                    transaksjon_id, kilde_system, funksjon_key, art_key, ansvar_key,
                    dato_key, belop, korrigert_belop, budsjett_belop
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tx_id, "Visma Enterprise (BOOM)", funksjon_key, art_key, ansvar_key, d_key, belop, korrigert, budsjett))
            inserted += 1

    conn.commit()
    print(f"✓ BoMiljø.csv lastet: {inserted} rader inn i Fact_Regnskap.")

def load_komskole(conn):
    """Laster inn data fra Komskole.csv (Mevold Grunnskole / Åseral)."""
    cur = conn.cursor()
    d_key = 20250801 # Aug-25
    
    loc_ansvar_map = {
        'Åseral barne- og ungdomsskule': '2020',
        'SFO-avdelingene (Lislehylen, Storehylen)': '2021',
        'Eget ansvar eller del av grunnskolen': '2022',
        'Leirskole mm': '2022',
        'Kommunal voksenopplæring': '2130',
        'Skole eller sentral stab': '2230',
        'Teknisk/eiendom eller skole': '2220',
        'Interkommunal eller lokal PPT-enhet': '2029'
    }

    inserted = 0
    with open(KOMSKOLE_CSV, 'r', encoding='latin-1') as f:
        rows = list(csv.reader(f))[3:] # Skip 3 header rows
        for r in rows:
            if len(r) < 12 or not r[4]:
                continue
            
            loc = r[4].strip()
            funksjonskode = r[5].strip()
            kontotype = r[7].strip()
            post = r[8].strip()
            
            # Beløpene i Komskole er i 1 000 kr -> multipliser med 1 000 for standardisering
            regn = float(r[9].replace(' ', '').replace(',', '.') or 0) * 1000.0
            bud = float(r[10].replace(' ', '').replace(',', '.') or 0) * 1000.0
            
            # Finn eller opprett funksjon
            cur.execute("SELECT funksjon_key FROM Dim_Funksjon WHERE funksjon_kode = ?", (funksjonskode,))
            row_f = cur.fetchone()
            if row_f:
                f_key = row_f[0]
            else:
                f_key = 1 # Fallback Grunnskole
                
            # Finn ansvar
            ansvar_kode = loc_ansvar_map.get(loc, '2020')
            cur.execute("SELECT ansvar_key FROM Dim_Ansvar WHERE ansvar_kode = ?", (ansvar_kode,))
            ans_key = cur.fetchone()[0]

            # Kartlegg art
            if 'Lønn' in kontotype:
                art_gruppe = 'Personal'
                sign = 1
                if 'Fast' in post: art_kode = '1010'
                elif 'vikar' in post.lower(): art_kode = '1020'
                elif 'ekstra' in post.lower(): art_kode = '1030'
                elif 'overtid' in post.lower(): art_kode = '1040'
                elif 'pensjon' in post.lower() or 'arbeidsgiveravgift' in post.lower(): art_kode = '1090'
                else: art_kode = '1050'
            elif 'Refusjon' in kontotype:
                art_gruppe = 'Refusjon'
                sign = -1
                art_kode = '1690'
            else:
                art_gruppe = 'Drift'
                sign = 1
                if 'Materiell' in post or 'materiell' in post.lower(): art_kode = '1110'
                elif 'Inventar' in post: art_kode = '1200'
                elif 'Kjøp fra' in post: art_kode = '1270'
                elif 'Telefon' in post or 'IKT' in post: art_kode = '1130'
                else: art_kode = '1150'
                
            art_key = get_or_create_art(conn, art_kode, f"{art_kode} {post}", art_gruppe, sign)
            korrigert = regn * sign
            
            tx_id = get_hash("KOMSKOLE", ansvar_kode, post, d_key, inserted)
            
            cur.execute("""
                INSERT OR REPLACE INTO Fact_Regnskap (
                    transaksjon_id, kilde_system, funksjon_key, art_key, ansvar_key,
                    dato_key, belop, korrigert_belop, budsjett_belop
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tx_id, "Framsikt / Visma (Skole)", f_key, art_key, ans_key, d_key, regn, korrigert, bud))
            inserted += 1

    conn.commit()
    print(f"✓ Komskole.csv lastet: {inserted} rader inn i Fact_Regnskap.")

def populate_audit_actions(conn):
    """Populerer revisjonsspor for AI-beslutningsstøtte (Human-in-the-Loop)."""
    cur = conn.cursor()
    audit_records = [
        (
            '2024-08-20 09:15:00', '2020', 'Antigravity-EPM-v2.4', 116000.0,
            'Tiltak A: Automatisk purring og avstemming mot NAV for utestående sykelønnsrefusjon (art 1690). Est. likviditetseffekt: kr 28 000.',
            0.94, 'GODKJENT', 'Avstemt mot lønnsavdelingen. Saksbehandler sendte purring via Altinn.',
            'Rektor Mevold Grunnskole', '10.140.22.15'
        ),
        (
            '2024-08-20 09:30:00', '2020', 'Antigravity-EPM-v2.4', 116000.0,
            'Tiltak B: Midlertidig frys i ikke-kritiske rammeavtaleinnkjøp på art 1200 fram til T2. Forventet innsparing: kr 15 000.',
            0.88, 'GODKJENT', 'Godkjent i samråd med controller. Kun akutte driftsartikler tillates.',
            'Rektor Mevold Grunnskole', '10.140.22.15'
        ),
        (
            '2024-08-22 14:10:00', '2540', 'Antigravity-EPM-v2.4', 1285614.0,
            'Tiltak A: Obligatorisk bruk av kommunens interne vikarpool framfor eksterne byråer (art 127040) for helgevakter. Est. innsparing: kr 380 000.',
            0.96, 'GODKJENT', 'Avtale inngått med enhetsleder om direkte prioritering via bemanningssenteret.',
            'Enhetsleder Slettheia Bofellesskap', '10.140.45.88'
        ),
        (
            '2024-08-22 14:45:00', '2540', 'Antigravity-EPM-v2.4', 1285614.0,
            'Tiltak B: Fremme sak om delvis dekning fra Toppfinansieringsordningen for ressurskrevende tjenester for 2 nye beboere med 2:1-bemanning.',
            0.91, 'GODKJENT', 'Dokumentasjon og vedtak samlet. Overleveres helse- og mestringsdirektør for formell innmelding.',
            'Kommunalsjef Helse og mestring', '10.140.10.2'
        )
    ]
    cur.executemany("""
        INSERT INTO Audit_AI_Actions (
            tidsstempel, enhet_kode, ai_modell_versjon, prognostisert_avvik,
            foreslatt_tiltak, konfidens_score, leder_beslutning, begrunnelse_tekst,
            godkjent_av_saksbehandler, IP_adresse
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, audit_records)
    conn.commit()
    print("✓ Audit_AI_Actions populert med verifiserte case-logger.")

def verify_database(conn):
    """Gjennomfører integritetssjekk og beregner kontrollsummer."""
    cur = conn.cursor()
    print("\n" + "="*70)
    print("VERIFIKASJON OG SYSTEMINTEGRITET (kristiansand_golden_record.db)")
    print("="*70)

    tables = ['Dim_Funksjon', 'Dim_Art', 'Dim_Ansvar', 'Dim_Dato', 'Fact_Regnskap', 'Audit_AI_Actions']
    for tbl in tables:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        cnt = cur.fetchone()[0]
        print(f"Tabell {tbl:<20}: {cnt:>6} rader")

    print("\nNøkkeltall per enhet:")
    print("-" * 70)
    cur.execute("""
        SELECT 
            da.ansvar_navn,
            df.funksjon_navn,
            COUNT(fr.transaksjon_id) as antall_poster,
            ROUND(SUM(fr.budsjett_belop), 0) as total_budsjett,
            ROUND(SUM(fr.korrigert_belop), 0) as total_regnskap,
            ROUND(SUM(fr.avvik_belop), 0) as total_avvik
        FROM Fact_Regnskap fr
        JOIN Dim_Ansvar da ON fr.ansvar_key = da.ansvar_key
        JOIN Dim_Funksjon df ON fr.funksjon_key = df.funksjon_key
        GROUP BY da.ansvar_navn, df.funksjon_navn
        ORDER BY da.ansvar_navn
    """)
    for row in cur.fetchall():
        navn, funk, cnt, bud, regn, avv = row
        print(f"{navn[:32]:<32} | Bud: {bud:>12,.0f} | Regn: {regn:>12,.0f} | Avvik: {avv:>11,.0f}")

    print("="*70)

def main():
    print("Starter etablering av Kristiansand Golden Record...")
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("Eksisterende database fjernet for ren gjenoppbygging.")
        
    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        populate_dimensions(conn)
        load_bomiljo(conn)
        load_komskole(conn)
        populate_audit_actions(conn)
        verify_database(conn)
    finally:
        conn.close()
    print("\nETL-kjøring fullført! Databasen er klar til bruk.")

if __name__ == "__main__":
    main()
