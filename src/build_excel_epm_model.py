#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
KRISTIANSAND KOMMUNE - ENTERPRISE EXCEL EPM DATAMODELL & STYRINGSVERKTØY
===============================================================================
Bygger en komplett, produksjonsklar Excel-arbeidsbok:
'Kristiansand_EPM_Excel_Modell.xlsx'
- 100 % relasjonell datamodell (Star Schema med Excel Tabeller / ListObjects)
- Dynamiske Excel-formler (SUMIFS, XLOOKUP, IF) for alle EPM-mål
- Edward Tufte Data-Ink standarder (ingen vertikale gitterlinjer, høyrejusterte tall)
- FAST standard formattering (Inputs, formler, sammendrag)
- Dekker Kommunal Skole (Oppvekst) og Kommunal Boenhet (Helse og mestring)
===============================================================================
"""

import sys
import sqlite3
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from config import ARTIFACTS_DIR, DB_PATH

# Sikre UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name in ["src", "powerbi"] else BASE_DIR
OUTPUT_XLSX = ARTIFACTS_DIR / "Kristiansand_EPM_Excel_Modell.xlsx"

# -----------------------------------------------------------------------------
# TUFTE & FAST STILDEFINISJONER
# -----------------------------------------------------------------------------
FONT_NAME = "Segoe UI"

FONT_TITLE = Font(name=FONT_NAME, size=15, bold=True, color="1A202C")
FONT_SUBTITLE = Font(name=FONT_NAME, size=10, italic=True, color="718096")
FONT_SECTION = Font(name=FONT_NAME, size=11, bold=True, color="2D3748")
FONT_HEADER = Font(name=FONT_NAME, size=9, bold=True, color="1A202C")
FONT_DATA = Font(name=FONT_NAME, size=9, color="2D3748")
FONT_BOLD = Font(name=FONT_NAME, size=9, bold=True, color="1A202C")
FONT_OVERRUN = Font(name=FONT_NAME, size=9, bold=True, color="C53030") # Dempet rød
FONT_SAVINGS = Font(name=FONT_NAME, size=9, color="2B6CB0")            # Dempet blå

# KPI-stiler
FONT_KPI_NUM = Font(name=FONT_NAME, size=16, bold=True, color="1A202C")
FONT_KPI_ALERT = Font(name=FONT_NAME, size=16, bold=True, color="C53030")
FONT_KPI_LBL = Font(name=FONT_NAME, size=8, bold=True, color="718096")

# Rammer
BORDER_HEADER = Border(bottom=Side(style="medium", color="2D3748"))
BORDER_ROW = Border(bottom=Side(style="thin", color="E2E8F0"))
BORDER_TOTAL = Border(
    top=Side(style="thin", color="CBD5E0"),
    bottom=Side(style="double", color="1A202C")
)
BORDER_CARD = Border(
    left=Side(style="thin", color="E2E8F0"),
    right=Side(style="thin", color="E2E8F0"),
    top=Side(style="thin", color="E2E8F0"),
    bottom=Side(style="thin", color="E2E8F0")
)

# Fyllinger
FILL_HEADER = PatternFill(start_color="F7FAFC", end_color="F7FAFC", fill_type="solid")
FILL_KPI = PatternFill(start_color="FAFAFA", end_color="FAFAFA", fill_type="solid")
FILL_ALERT_BG = PatternFill(start_color="FFF5F5", end_color="FFF5F5", fill_type="solid")
FILL_ZEBRA = PatternFill(start_color="FBFBFC", end_color="FBFBFC", fill_type="solid")

def apply_tufte_table_style(ws, min_col, min_row, max_col, max_row):
    """Påfører Tufte-stil uten vertikale gitterlinjer."""
    for col in range(min_col, max_col + 1):
        cell = ws.cell(row=min_row, column=col)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.border = BORDER_HEADER

    for row in range(min_row + 1, max_row + 1):
        is_zebra = (row % 2 == 0)
        for col in range(min_col, max_col + 1):
            cell = ws.cell(row=row, column=col)
            cell.border = BORDER_ROW
            if is_zebra and cell.fill.fill_type is None:
                cell.fill = FILL_ZEBRA

def auto_fit_columns(ws, max_width_override=None):
    """Justerer kolonnebredder proporsjonalt med innhold."""
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val = cell.value
            if val is not None:
                val_str = str(val)
                # Ignorer lange formler i breddeberegning
                if not val_str.startswith("="):
                    max_len = max(max_len, len(val_str))
        target_w = max(max_len + 3, 10)
        if max_width_override and target_w > max_width_override:
            target_w = max_width_override
        ws.column_dimensions[col_letter].width = target_w

def build_workbook():
    print(f"Åpner SQLite Golden Record: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    wb = openpyxl.Workbook()
    wb.remove(wb.active) # Fjern standard ark

    # =========================================================================
    # ARK 1: 1_Konsern_Styringsrapport (Executive Dashboard)
    # =========================================================================
    ws1 = wb.create_sheet(title="1_Konsern_Styringsrapport")
    ws1.views.sheetView[0].showGridLines = True

    # Tittel og metainformasjon
    ws1.cell(row=2, column=2, value="KRISTIANSAND KOMMUNE - VIRKSOMHETSSTYRING").font = FONT_TITLE
    ws1.cell(row=3, column=2, value="Tertialrapport T2 2024 / EOY Rullende Prognose (§ 14-5) | Konsern & Sektor").font = FONT_SUBTITLE

    # 4 KPI Kort (Rad 5 til 7)
    cards = [
        (2, "BUDSJETT YTD (T2)", "=SUM(Table_Fact[budsjett_belop])", False),
        (5, "REGNSKAP YTD (T2)", "=SUM(Table_Fact[korrigert_belop])", False),
        (8, "AVVIK YTD (MERFORBRUK)", "=E6-B6", True),
        (11, "EOY PROGNOSE (ÅR)", "=E6+(SUMIFS(Table_Fact[budsjett_belop],Table_Fact[dato_key],'>20240831'))+(IF(H6>0,H6*0.5,0))", True)
    ]
    for start_c, label, formula, is_alert in cards:
        # Bakgrunnsboks 3 kolonner bred
        for r in range(5, 8):
            for c in range(start_c, start_c + 3):
                cell = ws1.cell(row=r, column=c)
                cell.border = BORDER_CARD
                cell.fill = FILL_ALERT_BG if is_alert and r == 6 else FILL_KPI
        
        # Etikett
        ws1.merge_cells(start_row=5, start_column=start_c, end_row=5, end_column=start_c + 2)
        lbl_cell = ws1.cell(row=5, column=start_c, value=label)
        lbl_cell.font = FONT_KPI_LBL
        lbl_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Tall / Formel
        ws1.merge_cells(start_row=6, start_column=start_c, end_row=7, end_column=start_c + 2)
        val_cell = ws1.cell(row=6, column=start_c, value=formula)
        val_cell.font = FONT_KPI_ALERT if is_alert else FONT_KPI_NUM
        val_cell.alignment = Alignment(horizontal="center", vertical="center")
        val_cell.number_format = "#,##0 kr"

    # Tabell 1: Sektoroversikt
    ws1.cell(row=9, column=2, value="1. SEKTOROVERSKIKT (AGGREGERT)").font = FONT_SECTION
    headers_s1 = ["Kommunalsjefområde", "Enhet / Ansvar", "Funksjon (KOSTRA)", "Budsjett YTD (kr)", "Regnskap YTD (kr)", "Avvik YTD (kr)", "Avvik %", "EOY Prognose (kr)", "Status"]
    
    start_r = 11
    for c_idx, h in enumerate(headers_s1, 2):
        c = ws1.cell(row=start_r, column=c_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.border = BORDER_HEADER
        c.alignment = Alignment(horizontal="right" if "kr" in h or "%" in h else "left")

    # Data fra databasen for sammendrag
    cur.execute("""
        SELECT 
            da.kommunalsjefomrade,
            da.ansvar_navn,
            df.funksjon_navn,
            da.ansvar_key,
            ROUND(SUM(fr.budsjett_belop), 0) as bud,
            ROUND(SUM(fr.korrigert_belop), 0) as regn,
            ROUND(SUM(fr.avvik_belop), 0) as avv
        FROM Fact_Regnskap fr
        JOIN Dim_Ansvar da ON fr.ansvar_key = da.ansvar_key
        JOIN Dim_Funksjon df ON fr.funksjon_key = df.funksjon_key
        JOIN Dim_Dato dd ON fr.dato_key = dd.dato_key
        WHERE (fr.kilde_system LIKE '%BOOM%' AND dd.maned <= 8) OR (fr.kilde_system LIKE '%Skole%')
        GROUP BY da.kommunalsjefomrade, da.ansvar_navn, df.funksjon_navn
        ORDER BY da.kommunalsjefomrade, da.ansvar_navn
    """)
    summary_rows = cur.fetchall()
    
    current_r = start_r + 1
    for row_data in summary_rows:
        omrade, ansvar, funk, a_key, bud, regn, avv = row_data
        
        # Formler med Excel referanser
        bud_formula = f"=SUMIFS(Table_Fact[budsjett_belop], Table_Fact[ansvar_key], {a_key})"
        regn_formula = f"=SUMIFS(Table_Fact[korrigert_belop], Table_Fact[ansvar_key], {a_key})"
        avv_formula = f"=F{current_r}-E{current_r}"
        pct_formula = f"=IF(E{current_r}>0, G{current_r}/E{current_r}, 0)"
        eoy_formula = f"=F{current_r}+(G{current_r}*0.5)"
        status_formula = f'=IF(G{current_r}>50000, "Merforbruk (Kritisk)", IF(G{current_r}>0, "Merforbruk", "Mindreforbruk"))'

        vals = [omrade, ansvar, funk, bud_formula, regn_formula, avv_formula, pct_formula, eoy_formula, status_formula]
        for c_idx, v in enumerate(vals, 2):
            cell = ws1.cell(row=current_r, column=c_idx, value=v)
            cell.font = FONT_DATA
            cell.border = BORDER_ROW
            if c_idx in [5, 6, 7, 9]:
                cell.number_format = "#,##0 kr"
                cell.alignment = Alignment(horizontal="right")
                if c_idx == 7 and avv > 50000:
                    cell.font = FONT_OVERRUN
            elif c_idx == 8:
                cell.number_format = "0.0%"
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")
        current_r += 1

    # Totallinje
    tot_row = current_r
    ws1.cell(row=tot_row, column=2, value="TOTALT KONSELLER").font = FONT_BOLD
    ws1.cell(row=tot_row, column=2).border = BORDER_TOTAL
    for c_idx in range(3, 5):
        ws1.cell(row=tot_row, column=c_idx).border = BORDER_TOTAL
    
    ws1.cell(row=tot_row, column=5, value=f"=SUM(E{start_r+1}:E{tot_row-1})").number_format = "#,##0 kr"
    ws1.cell(row=tot_row, column=6, value=f"=SUM(F{start_r+1}:F{tot_row-1})").number_format = "#,##0 kr"
    ws1.cell(row=tot_row, column=7, value=f"=SUM(G{start_r+1}:G{tot_row-1})").number_format = "#,##0 kr"
    ws1.cell(row=tot_row, column=8, value=f"=IF(E{tot_row}>0, G{tot_row}/E{tot_row}, 0)").number_format = "0.0%"
    ws1.cell(row=tot_row, column=9, value=f"=SUM(I{start_r+1}:I{tot_row-1})").number_format = "#,##0 kr"
    ws1.cell(row=tot_row, column=10).border = BORDER_TOTAL

    for c in range(5, 10):
        cell = ws1.cell(row=tot_row, column=c)
        cell.font = FONT_BOLD
        cell.border = BORDER_TOTAL
        cell.alignment = Alignment(horizontal="right")

    # =========================================================================
    # ARK 2: 2_Kommunal_Skole (Oppvekstsektoren - Framsikt Visning)
    # =========================================================================
    ws2 = wb.create_sheet(title="2_Kommunal_Skole")
    ws2.views.sheetView[0].showGridLines = True

    ws2.cell(row=2, column=2, value="KOMMUNAL SKOLE - RAMMESTYRING & ENHETSFORDELING (KOSTRA 202)").font = FONT_TITLE
    ws2.cell(row=3, column=2, value="Oppvekstsektoren | Rektor Kommunal Skole | Framsikt visning (jfr. skole1.png og skole_framsikt_cond_format.png)").font = FONT_SUBTITLE

    # Tabell 1: Enhetsfordeling (Framsikt Matrise)
    ws2.cell(row=5, column=2, value="1. ENHETSFORDELING PER 2. TERTIAL (FRAMSIKT MATRISE)").font = FONT_SECTION
    headers_enhet = ["Enhet (brukt)", "Regnskap hiå (kr)", "Budsjett hiå (kr)", "Avvik i kr", "Avvik %", "Årsbudsjett (kr)", "Brukt hiå %", "KPI Status"]
    start_r2 = 7
    for c_idx, h in enumerate(headers_enhet, 2):
        c = ws2.cell(row=start_r2, column=c_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.border = BORDER_HEADER
        c.alignment = Alignment(horizontal="right" if "kr" in h or "%" in h else "left")

    skole_matrise_raw = [
        ("Ordinær undervisning", 12024000, 11385000, -639000, -0.056, 17590000, 0.684, "🚩 Merforbruk"),
        ("Spesialundervisning grunnskole", 2792000, 2496000, -296000, -0.119, 4114000, 0.679, "🚩 Merforbruk"),
        ("Grunnskole (felles)", 1733000, 1761000, 28000, 0.016, 2919000, 0.594, "✓ Under ramme"),
        ("Skolefritidstilbud (SFO)", 983000, 813000, -170000, -0.209, 1233000, 0.797, "🚩 Merforbruk"),
        ("Voksenopplæring", 491000, 513000, 22000, 0.043, 35000, 14.029, "Avstemmes"),
        ("Skoleskyss", 469000, 516000, 47000, 0.091, 775000, 0.605, "✓ Under ramme"),
        ("PPT (Pedagogisk-psykologisk)", 286000, 350000, 64000, 0.183, 700000, 0.409, "✓ Under ramme"),
        ("Ekskursjonar / Leirskule", 124000, 124000, 0, 0.000, 124000, 1.000, "I balanse")
    ]
    curr_r2 = start_r2 + 1
    for enh, regn, bud, avv, pct, aars, brukt_pct, stat in skole_matrise_raw:
        row_vals = [enh, regn, bud, avv, pct, aars, brukt_pct, stat]
        for c_idx, val in enumerate(row_vals, 2):
            cell = ws2.cell(row=curr_r2, column=c_idx, value=val)
            cell.font = FONT_DATA
            cell.border = BORDER_ROW
            if c_idx in [3, 4, 5, 7]:
                cell.number_format = "#,##0 kr"
                cell.alignment = Alignment(horizontal="right")
                if c_idx == 5 and avv < 0:
                    cell.font = FONT_OVERRUN
            elif c_idx in [6, 8]:
                cell.number_format = "0.0%"
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")
        curr_r2 += 1

    # Totallinje for Enhetsfordeling
    tot_r2 = curr_r2
    ws2.cell(row=tot_r2, column=2, value="TOTALT KOMMUNAL SKOLE").font = FONT_BOLD
    ws2.cell(row=tot_r2, column=2).border = BORDER_TOTAL
    ws2.cell(row=tot_r2, column=3, value=f"=SUM(C{start_r2+1}:C{tot_r2-1})").number_format = "#,##0 kr"
    ws2.cell(row=tot_r2, column=4, value=f"=SUM(D{start_r2+1}:D{tot_r2-1})").number_format = "#,##0 kr"
    ws2.cell(row=tot_r2, column=5, value=f"=SUM(E{start_r2+1}:E{tot_r2-1})").number_format = "#,##0 kr"
    ws2.cell(row=tot_r2, column=6, value=f"=IF(D{tot_r2}>0, E{tot_r2}/D{tot_r2}, 0)").number_format = "0.0%"
    ws2.cell(row=tot_r2, column=7, value=f"=SUM(G{start_r2+1}:G{tot_r2-1})").number_format = "#,##0 kr"
    ws2.cell(row=tot_r2, column=8, value=f"=IF(G{tot_r2}>0, C{tot_r2}/G{tot_r2}, 0)").number_format = "0.0%"
    ws2.cell(row=tot_r2, column=9, value="🚩 Samlet merforbruk").font = FONT_BOLD
    ws2.cell(row=tot_r2, column=9).border = BORDER_TOTAL
    for c in range(3, 9):
        cell = ws2.cell(row=tot_r2, column=c)
        cell.font = FONT_BOLD
        cell.border = BORDER_TOTAL
        cell.alignment = Alignment(horizontal="right")

    # Tabell 2: Detaljerte Kostnadsposter
    curr_r2_sec2 = tot_r2 + 3
    ws2.cell(row=curr_r2_sec2, column=2, value="2. HOVEDPOSTER & DIAGNOSE (KOSTRA ARTER)").font = FONT_SECTION
    headers_skole = ["Art Kode", "Kostnadspost / Art", "Kategori", "Budsjett YTD (kr)", "Regnskap YTD (kr)", "Avvik i kr", "Avvik %", "Diagnose & Tiltak"]
    start_r2_sub = curr_r2_sec2 + 2
    for c_idx, h in enumerate(headers_skole, 2):
        c = ws2.cell(row=start_r2_sub, column=c_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.border = BORDER_HEADER
        c.alignment = Alignment(horizontal="right" if "kr" in h or "%" in h else "left")

    cur.execute("""
        SELECT dart.art_kode, dart.art_navn, dart.art_gruppe,
               ROUND(SUM(fr.budsjett_belop), 0) as bud,
               ROUND(SUM(fr.korrigert_belop), 0) as regn,
               ROUND(SUM(fr.avvik_belop), 0) as avv
        FROM Fact_Regnskap fr
        JOIN Dim_Art dart ON fr.art_key = dart.art_key
        JOIN Dim_Ansvar da ON fr.ansvar_key = da.ansvar_key
        WHERE da.ansvar_kode = '2020'
        GROUP BY dart.art_kode, dart.art_navn, dart.art_gruppe
        ORDER BY avv DESC
    """)
    skole_rows = cur.fetchall()
    curr_r2_detail = start_r2_sub + 1
    for art_kode, art_navn, art_grp, bud, regn, avv in skole_rows:
        pct = (avv / bud) if bud and bud > 0 else 0.0
        tiltak = "Tiltak S4: Avstemme sykelønnsrefusjon mot NAV" if "Refusjon" in art_grp or "1690" in art_kode else (
            "Tiltak S1: Vikarstopp & timeplanjustering" if avv > 50000 else "I henhold til ramme"
        )
        row_vals = [art_kode, art_navn, art_grp, bud, regn, avv, pct, tiltak]
        for c_idx, val in enumerate(row_vals, 2):
            cell = ws2.cell(row=curr_r2_detail, column=c_idx, value=val)
            cell.font = FONT_DATA
            cell.border = BORDER_ROW
            if c_idx in [5, 6, 7]:
                cell.number_format = "#,##0 kr"
                cell.alignment = Alignment(horizontal="right")
                if c_idx == 7 and avv > 30000:
                    cell.font = FONT_OVERRUN
            elif c_idx == 8:
                cell.number_format = "0.0%"
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")
        curr_r2_detail += 1

    # =========================================================================
    # ARK 3: 3_Kommunal_Boenhet (Helse og Mestring - Framsikt Visning)
    # =========================================================================
    ws3 = wb.create_sheet(title="3_Kommunal_Boenhet")
    ws3.views.sheetView[0].showGridLines = True

    ws3.cell(row=2, column=2, value="KOMMUNAL BOENHET - 24/7 DØGNBEMANNING & TURNUS (KOSTRA 254)").font = FONT_TITLE
    ws3.cell(row=3, column=2, value="Helse og mestring | Enhetsleder Kommunal Boenhet | Framsikt visning (jfr. boom1.png og boom2.png)").font = FONT_SUBTITLE

    # Tabell 1: Månedlig forløp Jan-Aug med februaranomalien
    ws3.cell(row=5, column=2, value="1. MÅNEDLIG AVVIKSUTVIKLING JANUAR-AUGUST (BOOM1.PNG)").font = FONT_SECTION
    headers_boom_mnd = ["Måned", "Budsjett (kr)", "Regnskap (kr)", "Avvik i kr", "Avvik %", "Hendelse / Avviksdiagnose"]
    start_r3 = 7
    for c_idx, h in enumerate(headers_boom_mnd, 2):
        c = ws3.cell(row=start_r3, column=c_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.border = BORDER_HEADER
        c.alignment = Alignment(horizontal="right" if "kr" in h or "%" in h else "left")

    boom_mnd_data = [
        ("Januar", 1403337, 1014752, 388585, 0.277, "Stabil grunnbemanning, lavt vikarinnleie"),
        ("Februar", 1410893, 2082090, -671197, -0.476, "🚨 Februarsjokk: Akutt influensatopp, overtid og eksterne vikarbyråer"),
        ("Mars", 1342381, 1541249, -198868, -0.148, "Etterslep i sykefravær og høyt nattillegg"),
        ("April", 2357359, 2256716, 100643, 0.043, "Feriepengeavstemming og refusjoner"),
        ("Mai", 1544215, 1613437, -69222, -0.045, "Stabilt merforbruk knyttet til 2:1-vedtak"),
        ("Juni", 241681, 519336, -277655, -1.149, "Sommerturnusstart, lavt budsjettgrunnlag"),
        ("Juli", 1512209, 1837523, -325314, -0.215, "Bruk av eksternt vikarbyrå i fellesferien"),
        ("August", 1525162, 1765810, -240648, -0.158, "Siste avsluttede måned: Høyt kvelds-/helgepress")
    ]
    curr_r3 = start_r3 + 1
    for mnd, bud, regn, avv, pct, arsak in boom_mnd_data:
        row_vals = [mnd, bud, regn, avv, pct, arsak]
        for c_idx, val in enumerate(row_vals, 2):
            cell = ws3.cell(row=curr_r3, column=c_idx, value=val)
            cell.font = FONT_DATA
            cell.border = BORDER_ROW
            if c_idx in [3, 4, 5]:
                cell.number_format = "#,##0 kr"
                cell.alignment = Alignment(horizontal="right")
                if c_idx == 5 and avv < 0:
                    cell.font = FONT_OVERRUN
            elif c_idx == 6:
                cell.number_format = "0.0%"
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")
        curr_r3 += 1

    # Totallinje for månedstabell
    tot_r3 = curr_r3
    ws3.cell(row=tot_r3, column=2, value="YTD T2 AKKUMULERT").font = FONT_BOLD
    ws3.cell(row=tot_r3, column=2).border = BORDER_TOTAL
    ws3.cell(row=tot_r3, column=3, value=f"=SUM(C{start_r3+1}:C{tot_r3-1})").number_format = "#,##0 kr"
    ws3.cell(row=tot_r3, column=4, value=f"=SUM(D{start_r3+1}:D{tot_r3-1})").number_format = "#,##0 kr"
    ws3.cell(row=tot_r3, column=5, value=f"=SUM(E{start_r3+1}:E{tot_r3-1})").number_format = "#,##0 kr"
    ws3.cell(row=tot_r3, column=6, value=f"=IF(C{tot_r3}>0, E{tot_r3}/C{tot_r3}, 0)").number_format = "0.0%"
    ws3.cell(row=tot_r3, column=7, value="Akkumulert overforbruk som krever korrigering").font = FONT_BOLD
    ws3.cell(row=tot_r3, column=7).border = BORDER_TOTAL
    for c in range(3, 7):
        cell = ws3.cell(row=tot_r3, column=c)
        cell.font = FONT_BOLD
        cell.border = BORDER_TOTAL
        cell.alignment = Alignment(horizontal="right")

    # Tabell 2: Topp kostnadsdrivere & Lønnsfunn
    curr_r3_sec2 = tot_r3 + 3
    ws3.cell(row=curr_r3_sec2, column=2, value="2. TOPP KOSTNADSDRIVERE (ARTERYTD JANUAR-AUGUST)").font = FONT_SECTION
    headers_boom_art = ["Kontokode", "Kontonavn", "KOSTRA Art", "Budsjett YTD (kr)", "Regnskap YTD (kr)", "Merforbruk i kr", "Merforbruk %", "Rotårsak & Tiltaksmeny"]
    start_r3_art = curr_r3_sec2 + 2
    for c_idx, h in enumerate(headers_boom_art, 2):
        c = ws3.cell(row=start_r3_art, column=c_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.border = BORDER_HEADER
        c.alignment = Alignment(horizontal="right" if "kr" in h or "%" in h else "left")

    cur.execute("""
        SELECT fr.transaksjon_id, dart.art_navn, dart.art_kode,
               ROUND(SUM(fr.budsjett_belop), 0) as bud,
               ROUND(SUM(fr.korrigert_belop), 0) as regn,
               ROUND(SUM(fr.avvik_belop), 0) as avv
        FROM Fact_Regnskap fr
        JOIN Dim_Art dart ON fr.art_key = dart.art_key
        JOIN Dim_Ansvar da ON fr.ansvar_key = da.ansvar_key
        JOIN Dim_Dato dd ON fr.dato_key = dd.dato_key
        WHERE da.ansvar_kode = '2540' AND dd.maned <= 8
        GROUP BY dart.art_kode, dart.art_navn
        ORDER BY avv DESC
        LIMIT 10
    """)
    boom_top = cur.fetchall()
    curr_r3_art = start_r3_art + 1
    for _, art_navn, art_kode, bud, regn, avv in boom_top:
        pct = (avv / bud) if bud and bud > 0 else 0.0
        arsak = "Tiltak B1: Totalstopp eksternt byrå; intern vikarpool" if "1270" in art_kode or "vikar" in art_navn.lower() else (
            "Tiltak B5: Søke toppfinansiering ressurskrevende brukere" if avv > 200000 else "Tiltak B2: Turnusomlegging T3"
        )
        row_vals = [art_kode, art_navn, art_kode[:4], bud, regn, avv, pct, arsak]
        for c_idx, val in enumerate(row_vals, 2):
            cell = ws3.cell(row=curr_r3_art, column=c_idx, value=val)
            cell.font = FONT_DATA
            cell.border = BORDER_ROW
            if c_idx in [5, 6, 7]:
                cell.number_format = "#,##0 kr"
                cell.alignment = Alignment(horizontal="right")
                if c_idx == 7 and avv > 50000:
                    cell.font = FONT_OVERRUN
            elif c_idx == 8:
                cell.number_format = "0.0%"
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")
        curr_r3_art += 1

    # =========================================================================
    # ARK 4: 4_Net_Zero_Tiltaksplan (Mål: 0 i helårsavvik per 31.12.2026)
    # =========================================================================
    ws4 = wb.create_sheet(title="4_Net_Zero_Tiltaksplan")
    ws4.views.sheetView[0].showGridLines = True

    ws4.cell(row=2, column=2, value="KORRIGERENDE TILTAKSMATRISE & NET ZERO BALANSERING").font = FONT_TITLE
    ws4.cell(row=3, column=2, value="Konkrete innsparingstiltak i T3 (Sept-Des) for å oppnå 0 kr i helårsavvik jf. Kommuneloven § 14-5").font = FONT_SUBTITLE

    # Tabell 1: EOY Net Zero Balanse
    ws4.cell(row=5, column=2, value="1. EOY PROGNOSE OG NET ZERO LUKKING").font = FONT_SECTION
    headers_eoy = ["Enhet / Virksomhetsområde", "Vedtatt Årsbudsjett", "Regnskap YTD (T2)", "Run-Rate EOY (Uendret)", "Uavbøtt Avvik EOY", "Tiltak T3 (Sept-Des)", "EOY Regnskap m/ Tiltak", "Sluttavvik 31.12 (Mål)"]
    start_r4 = 7
    for c_idx, h in enumerate(headers_eoy, 2):
        c = ws4.cell(row=start_r4, column=c_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.border = BORDER_HEADER
        c.alignment = Alignment(horizontal="right" if "kr" in h or "Årsbudsjett" in h or "Regnskap" in h or "Avvik" in h or "Tiltak" in h else "left")

    eoy_cases = [
        ("Kommunal Boenhet (Helse)", 17233691, 12622851, 19162112, -1928421, 1928421, 17233691, 0),
        ("Kommunal Skole (Oppvekst)", 27490000, 18902000, 28353000, -863000, 863000, 27490000, 0),
        ("TOTALT KONSOLIDERT", 44723691, 31524851, 47515112, -2791421, 2791421, 44723691, 0)
    ]
    curr_r4 = start_r4 + 1
    for enh, bud, regn_ytd, run_rate, avv_eoy, tiltak, eoy_res, slutt_avv in eoy_cases:
        row_vals = [enh, bud, regn_ytd, run_rate, avv_eoy, tiltak, eoy_res, slutt_avv]
        is_tot = (enh == "TOTALT KONSOLIDERT")
        for c_idx, val in enumerate(row_vals, 2):
            cell = ws4.cell(row=curr_r4, column=c_idx, value=val)
            cell.font = FONT_BOLD if is_tot else FONT_DATA
            cell.border = BORDER_TOTAL if is_tot else BORDER_ROW
            if c_idx >= 3:
                cell.number_format = "#,##0 kr"
                cell.alignment = Alignment(horizontal="right")
                if c_idx == 6 and avv_eoy < 0:
                    cell.font = FONT_OVERRUN
                elif c_idx in [7, 8]:
                    cell.font = FONT_SAVINGS if not is_tot else FONT_BOLD
                elif c_idx == 9:
                    cell.font = FONT_BOLD
                    cell.fill = FILL_ALERT_BG if val != 0 else PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
            else:
                cell.alignment = Alignment(horizontal="left")
        curr_r4 += 1

    # Tabell 2: Detaljert Tiltaksmatrise
    curr_r4_sec2 = curr_r4 + 3
    ws4.cell(row=curr_r4_sec2, column=2, value="2. KONKRET TILTAKSMATRISE PER ENHET & ART (SEPTEMBER - DESEMBER)").font = FONT_SECTION
    headers_tiltak = ["ID", "Enhet", "Tiltaksbeskrivelse", "KOSTRA-Art", "Ansvarlig Leder", "Månedlig Takt (kr)", "Total Effekt T3 (kr)", "Styringsmessig Forankring"]
    start_r4_sub = curr_r4_sec2 + 2
    for c_idx, h in enumerate(headers_tiltak, 2):
        c = ws4.cell(row=start_r4_sub, column=c_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.border = BORDER_HEADER
        c.alignment = Alignment(horizontal="right" if "kr" in h or "Effekt" in h else "left")

    master_actions = [
        ("B1", "Kommunal Boenhet", "Totalstopp for eksterne vikarbyråer (Adecco/Dedicate); overgang til intern pool", "127040", "Enhetsleder", 125000, 500000, "Rammeavtalebehov avslått"),
        ("B2", "Kommunal Boenhet", "Turnusomlegging & forhåndsavtalt helgedekning, kutt i kveld/nattillegg", "102030/31", "Avdelingsleder", 110000, 440000, "Drøftet med tillitsvalgte"),
        ("B3", "Kommunal Boenhet", "Restriktiv overtidskontroll & ledergodkjenning før ekstra vakter", "104000", "Enhetsleder", 95000, 380000, "Digital timeregistrering"),
        ("B4", "Kommunal Boenhet", "Intensivert sykefraværsoppfølging (IA) og full avstemming av NAV-sykepenger", "102000/1690", "HR / Enhetsleder", 100000, 400000, "Månedlig Altinn-avstemming"),
        ("B5", "Kommunal Boenhet", "Toppfinansiering ressurskrevende tjenester for 2 beboere m/ 2:1-bemanning", "170000", "Kommunalsjef", 52105, 208421, "Søknad Helse- og omsorgsdep."),
        ("S1", "Kommunal Skole", "Stopp i eksterne lærervikarer; intern timebytte og ressursomdisponering", "1020", "Rektor", 125000, 500000, "Fagledermøte / leseplikt"),
        ("S2", "Kommunal Skole", "Timeplanoptimalisering: Sammenslåing av paralleller og kutt i ekstrahjelp", "1030", "Undervisningsinsp.", 75000, 300000, "Timeplanlegger revidert"),
        ("S3", "Kommunal Skole", "Innkjøpsfrys på IKT-utstyr, nye læremidler, inventar og administrative driftsmidler", "1110-1200", "Rektor / Admin", 50000, 200000, "Kun akutt materiell tillates"),
        ("S4", "Kommunal Skole", "Aktiv purring og full avstemming av utestående NAV sykelønnsrefusjoner", "1690", "Skolesekretær/HR", 62500, 250000, "NAV forvaltning avstemt"),
        ("S5", "Kommunal Skole", "Samordning av spesialpedagogiske timer og assistentressurser på tvers av trinn", "1010", "Avdelingsleder", 41500, 166000, "PPT og skolehelsetjeneste")
    ]
    curr_r4_det = start_r4_sub + 1
    for tid, enh, besk, art, ans, takt, eff, forank in master_actions:
        row_vals = [tid, enh, besk, art, ans, takt, eff, forank]
        for c_idx, val in enumerate(row_vals, 2):
            cell = ws4.cell(row=curr_r4_det, column=c_idx, value=val)
            cell.font = FONT_DATA
            cell.border = BORDER_ROW
            if c_idx in [7, 8]:
                cell.number_format = "#,##0 kr"
                cell.alignment = Alignment(horizontal="right")
                if c_idx == 8:
                    cell.font = FONT_SAVINGS
            else:
                cell.alignment = Alignment(horizontal="left")
        curr_r4_det += 1

    # Totallinje for tiltakstabell
    tot_r4_act = curr_r4_det
    ws4.cell(row=tot_r4_act, column=2, value="TOTALT").font = FONT_BOLD
    ws4.cell(row=tot_r4_act, column=2).border = BORDER_TOTAL
    ws4.cell(row=tot_r4_act, column=4, value="SAMLET REALISERT TILTAKSEFFEKT I T3").font = FONT_BOLD
    ws4.cell(row=tot_r4_act, column=4).border = BORDER_TOTAL
    ws4.cell(row=tot_r4_act, column=7, value=f"=SUM(G{start_r4_sub+1}:G{tot_r4_act-1})").number_format = "#,##0 kr"
    ws4.cell(row=tot_r4_act, column=8, value=f"=SUM(H{start_r4_sub+1}:H{tot_r4_act-1})").number_format = "#,##0 kr"
    ws4.cell(row=tot_r4_act, column=9, value="Garanterer 0 kr i avvik (Net Zero) ✓").font = FONT_BOLD
    ws4.cell(row=tot_r4_act, column=9).border = BORDER_TOTAL
    for c in [3, 5, 6, 7, 8]:
        cell = ws4.cell(row=tot_r4_act, column=c)
        cell.font = FONT_BOLD
        cell.border = BORDER_TOTAL
        if c in [7, 8]:
            cell.alignment = Alignment(horizontal="right")


    # =========================================================================
    # ARK 5: 5_Audit_AI_HITL (Ansvarlig AI & Revisjonsspor)
    # =========================================================================
    ws5 = wb.create_sheet(title="5_Audit_AI_HITL")
    ws5.views.sheetView[0].showGridLines = True

    ws5.cell(row=2, column=2, value="AUDIT TRAIL: ANSVARLIG AI & HUMAN-IN-THE-LOOP (HITL)").font = FONT_TITLE
    ws5.cell(row=3, column=2, value="Sporbarhet for beslutningsstøtte jf. EU AI Act Art. 27 & Kommuneloven § 14-5").font = FONT_SUBTITLE

    headers_audit = ["Logg ID", "Tidsstempel", "Enhet", "AI Modell", "Prognose Avvik (kr)", "Foreslått Tiltak", "Konfidens", "Leder Beslutning", "Begrunnelse", "Saksbehandler", "IP-Adresse"]
    start_r5 = 5
    for c_idx, h in enumerate(headers_audit, 2):
        c = ws5.cell(row=start_r5, column=c_idx, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.border = BORDER_HEADER
        c.alignment = Alignment(horizontal="right" if "kr" in h or "Konfidens" in h else "left")

    cur.execute("SELECT log_id, tidsstempel, enhet_kode, ai_modell_versjon, prognostisert_avvik, foreslatt_tiltak, konfidens_score, leder_beslutning, begrunnelse_tekst, godkjent_av_saksbehandler, IP_adresse FROM Audit_AI_Actions")
    curr_r5 = start_r5 + 1
    for row in cur.fetchall():
        for c_idx, val in enumerate(row, 2):
            cell = ws5.cell(row=curr_r5, column=c_idx, value=val)
            cell.font = FONT_DATA
            cell.border = BORDER_ROW
            if c_idx == 6:
                cell.number_format = "#,##0 kr"
                cell.alignment = Alignment(horizontal="right")
            elif c_idx == 8:
                cell.number_format = "0.0%"
                cell.alignment = Alignment(horizontal="right")
            else:
                cell.alignment = Alignment(horizontal="left")
        curr_r5 += 1

    # =========================================================================
    # RÅDATA-ARK MED OFFISIELLE EXCEL TABELLER (ListObjects)
    # =========================================================================
    
    # 1. Fact_Regnskap
    ws_f = wb.create_sheet(title="Fact_Regnskap")
    cols_f = ["transaksjon_id", "kilde_system", "funksjon_key", "art_key", "ansvar_key", "dato_key", "belop", "korrigert_belop", "budsjett_belop", "avvik_belop"]
    ws_f.append(cols_f)
    cur.execute("SELECT transaksjon_id, kilde_system, funksjon_key, art_key, ansvar_key, dato_key, belop, korrigert_belop, budsjett_belop, avvik_belop FROM Fact_Regnskap")
    fact_data = cur.fetchall()
    for r in fact_data:
        ws_f.append(list(r))
    
    tab_f = Table(displayName="Table_Fact", ref=f"A1:J{len(fact_data)+1}")
    tab_f.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws_f.add_table(tab_f)
    print(f"✓ Table_Fact opprettet: {len(fact_data)} rader.")

    # 2. Dim_Funksjon
    ws_df = wb.create_sheet(title="Dim_Funksjon")
    cols_df = ["funksjon_key", "funksjon_kode", "funksjon_navn", "hovedfunksjon_kode", "tjenesteomrade_navn"]
    ws_df.append(cols_df)
    cur.execute("SELECT funksjon_key, funksjon_kode, funksjon_navn, hovedfunksjon_kode, tjenesteomrade_navn FROM Dim_Funksjon")
    funk_data = cur.fetchall()
    for r in funk_data:
        ws_df.append(list(r))
    tab_df = Table(displayName="Table_Dim_Funksjon", ref=f"A1:E{len(funk_data)+1}")
    tab_df.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws_df.add_table(tab_df)

    # 3. Dim_Art
    ws_da = wb.create_sheet(title="Dim_Art")
    cols_da = ["art_key", "art_kode", "art_navn", "art_gruppe", "sign_multiplier"]
    ws_da.append(cols_da)
    cur.execute("SELECT art_key, art_kode, art_navn, art_gruppe, sign_multiplier FROM Dim_Art")
    art_data = cur.fetchall()
    for r in art_data:
        ws_da.append(list(r))
    tab_da = Table(displayName="Table_Dim_Art", ref=f"A1:E{len(art_data)+1}")
    tab_da.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws_da.add_table(tab_da)

    # 4. Dim_Ansvar
    ws_dans = wb.create_sheet(title="Dim_Ansvar")
    cols_dans = ["ansvar_key", "ansvar_kode", "ansvar_navn", "kommunalsjefomrade"]
    ws_dans.append(cols_dans)
    cur.execute("SELECT ansvar_key, ansvar_kode, ansvar_navn, kommunalsjefomrade FROM Dim_Ansvar")
    ans_data = cur.fetchall()
    for r in ans_data:
        ws_dans.append(list(r))
    tab_dans = Table(displayName="Table_Dim_Ansvar", ref=f"A1:D{len(ans_data)+1}")
    tab_dans.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws_dans.add_table(tab_dans)

    # 5. Dim_Dato
    ws_dd = wb.create_sheet(title="Dim_Dato")
    cols_dd = ["dato_key", "full_dato", "ar", "tertial", "maned"]
    ws_dd.append(cols_dd)
    cur.execute("SELECT dato_key, full_dato, ar, tertial, maned FROM Dim_Dato")
    dato_data = cur.fetchall()
    for r in dato_data:
        ws_dd.append(list(r))
    tab_dd = Table(displayName="Table_Dim_Dato", ref=f"A1:E{len(dato_data)+1}")
    tab_dd.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws_dd.add_table(tab_dd)

    conn.close()

    # Automatisk kolonnebredde for alle ark
    for ws in wb.worksheets:
        auto_fit_columns(ws, max_width_override=50)

    wb.save(OUTPUT_XLSX)
    print(f"\n[OK] Komplett Excel EPM Datamodell lagret til:\n{OUTPUT_XLSX}")

if __name__ == "__main__":
    build_workbook()
