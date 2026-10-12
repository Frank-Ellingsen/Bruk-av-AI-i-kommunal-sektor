#!/usr/bin/env python3
"""
Human-in-the-Loop (HITL) Governance & Excel Writeback Module
Audits decisions into SQLite/DuckDB and writes approved measures back to the Excel model.
"""

from pathlib import Path
from datetime import datetime
import sqlite3
import shutil
import openpyxl

try:
    from config import EXCEL_SOURCE, EXCEL_OUTPUT, DB_SQLITE, DEFAULT_ENHET, DEFAULT_SAKSBEHANDLER
    from prescriptive_agent import DEFAULT_CANDIDATE_MEASURES
except ImportError:
    from mvp_pilot.config import EXCEL_SOURCE, EXCEL_OUTPUT, DB_SQLITE, DEFAULT_ENHET, DEFAULT_SAKSBEHANDLER
    from mvp_pilot.prescriptive_agent import DEFAULT_CANDIDATE_MEASURES


def record_audit_action(
    enhet_kode: str,
    ai_model: str,
    measure_id: str,
    measure_title: str,
    estimated_effect: float,
    confidence_score: float,
    decision: str,
    control_documented: str,
    justification: str,
    approved_by: str,
    db_path: Path = DB_SQLITE
):
    """Lagrer et formelt revisjonsspor i Audit_AI_Actions tabellen."""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO Audit_AI_Actions (
            enhet_kode, ai_model, measure_id, measure_title, estimated_effect,
            confidence_score, decision, control_documented, justification, approved_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        enhet_kode, ai_model, measure_id, measure_title, estimated_effect,
        confidence_score, decision, control_documented, justification, approved_by
    ))
    con.commit()
    con.close()
    print(f"[AUDIT] Vedtak logget for tiltak {measure_id}: {decision} av {approved_by}")


def apply_decisions_and_writeback(
    decisions_dict: dict,
    target_excel: Path = EXCEL_SOURCE,
    create_backup: bool = True,
    approved_by: str = DEFAULT_SAKSBEHANDLER
) -> dict:
    """
    Oppdaterer Excel-arket '3 AI tiltak og effekt' med godkjenninger.
    
    decisions_dict format:
    {
        'T1': {'decision': 'Godkjent', 'control_documented': 'Ja', 'justification': 'Avstemt mot NAV'},
        'T2': {'decision': 'Kandidat', 'control_documented': 'Nei', 'justification': 'Drøfting pågår'},
        ...
    }
    """
    if not target_excel.exists():
        raise FileNotFoundError(f"Excel-fil ikke funnet: {target_excel}")

    if create_backup:
        backup_path = target_excel.parent / f"{target_excel.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        shutil.copy2(target_excel, backup_path)
        print(f"[HITL] Sikkerhetskopi opprettet: {backup_path.name}")

    wb = openpyxl.load_workbook(target_excel, data_only=False)
    sheet_name = "3 AI tiltak og effekt"
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Finner ikke arket '{sheet_name}' i Excel-filen.")

    ws = wb[sheet_name]

    # Map rader 6 til 11
    total_godkjent_effekt = 0.0
    antall_godkjente = 0

    measures_by_id = {m["id"]: m for m in DEFAULT_CANDIDATE_MEASURES}

    for r in range(6, 12):
        mid = str(ws.cell(r, 1).value).strip()
        if mid in decisions_dict:
            dec_info = decisions_dict[mid]
            status = dec_info.get("decision", "Kandidat")
            kontroll = dec_info.get("control_documented", "Nei")
            begrunnelse = dec_info.get("justification", "")

            # Kolonne M: Beslutning
            ws.cell(r, 13).value = status
            # Kolonne N: Kontroll dokumentert
            ws.cell(r, 14).value = kontroll

            # Hvis neste steg / begrunnelse oppgitt
            if begrunnelse:
                ws.cell(r, 16).value = f"{ws.cell(r, 16).value or ''} | Notat: {begrunnelse}".strip(" |")

            # Hent effekt hvis godkjent
            effekt = float(ws.cell(r, 8).value or 0.0)
            if status == "Godkjent" and kontroll == "Ja":
                total_godkjent_effekt += effekt
                antall_godkjente += 1

            # Logg til audit-tabell
            m_meta = measures_by_id.get(mid, {})
            record_audit_action(
                enhet_kode=DEFAULT_ENHET,
                ai_model="Ollama llama3.1 (Prescriptive Agent)",
                measure_id=mid,
                measure_title=m_meta.get("title", f"Tiltak {mid}"),
                estimated_effect=effekt,
                confidence_score=m_meta.get("probability", 0.8),
                decision=status,
                control_documented=kontroll,
                justification=begrunnelse,
                approved_by=approved_by
            )

    wb.save(target_excel)
    print(f"[HITL] Excel-oppdatering fullført: {target_excel.name}")
    print(f"       • Godkjente tiltak: {antall_godkjente}")
    print(f"       • Samlet godkjent EOY-effekt: {total_godkjent_effekt:,.2f} kr")

    return {
        "target_file": str(target_excel),
        "antall_godkjente": antall_godkjente,
        "godkjent_effekt": total_godkjent_effekt
    }


if __name__ == "__main__":
    # Eksempel på en godkjenningskjøring for piloten
    test_decisions = {
        "T1": {
            "decision": "Godkjent",
            "control_documented": "Ja",
            "justification": "Krav avstemt mot NAV refusjonsportal; 41k bekreftet."
        },
        "T2": {
            "decision": "Godkjent",
            "control_documented": "Ja",
            "justification": "Drøftet med tillitsvalgt iht. HTA § 4; vikarstopp på dagtid."
        }
    }
    apply_decisions_and_writeback(test_decisions, create_backup=False)
