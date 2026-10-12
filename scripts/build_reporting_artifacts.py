import json
import math
import shutil
import uuid
from pathlib import Path

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import CellIsRule, DataBarRule, FormulaRule, IconSetRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path('/workspaces/use cases')
DATA_DIR = ROOT / 'data'
POWERBI_DIR = ROOT / 'powerbi' / 'projects'

MEASURES = [
    'Regnskap YTD',
    'Budsjett YTD',
    'Avvik YTD',
    'Avvik YTD %',
    'Merforbruk YTD',
    'Mindreforbruk YTD',
    'Vedtatt Årsbudsjett',
    'EOY Rullende Prognose',
    'EOY Forventet Årsavvik',
    'Brutto Driftsresultat',
    'Brutto Driftsresultat %',
    'Tufte_Avvik_Farge_HEX',
    'Planlagt Tiltakseffekt T3',
    'Framsikt Deflator Value',
    'Fraværstiltak Effektreduksjon Value',
    'Simulert EOY Netto Driftsresultat',
    'Simulert EOY Forventet Avvik',
    'EOY Net Zero Sluttavvik',
]


def set_title(ws, title, subtitle=''):
    ws.merge_cells('A1:F1')
    ws['A1'] = title
    ws['A1'].font = Font(bold=True, size=16, color='FFFFFF')
    ws['A1'].fill = PatternFill('solid', fgColor='1B365D')
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    if subtitle:
        ws.merge_cells('A2:F2')
        ws['A2'] = subtitle
        ws['A2'].font = Font(italic=True, color='4A77A0')
        ws['A2'].alignment = Alignment(horizontal='center')


def format_table_headers(ws, row_index=5):
    header_fill = PatternFill('solid', fgColor='D9EAF7')
    header_font = Font(bold=True, color='1B365D')
    for cell in ws[row_index]:
        cell.fill = header_fill
        cell.font = header_font
        cell.border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9'),
        )


def add_kpi(ws, row, label, value, format_str='kr', color='1B365D'):
    ws[f'A{row}'] = label
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'B{row}'] = value
    ws[f'B{row}'].font = Font(bold=True, size=12, color=color)
    ws[f'B{row}'].number_format = format_str


def build_bo_miljo_workbook(output_path: Path):
    df = pd.read_csv(DATA_DIR / 'BoMiljø.csv', encoding='utf-8-sig')
    df['Budsjett'] = pd.to_numeric(df['Budsjett'], errors='coerce').fillna(0)
    df['Regnskap'] = pd.to_numeric(df['Regnskap'], errors='coerce').fillna(0)
    df['Avvik'] = df['Regnskap'] - df['Budsjett']
    df['Merforbruk'] = df['Avvik'].clip(lower=0)
    df_ytd = df[df['Måned_Nr'] <= 8].copy()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Overview'
    set_title(ws, 'Kommunal Boenhet - EPM Rapport', 'YTD performance vs budsjett og egenmålt framsiktsprognose')

    total_regnskap = float(df_ytd['Regnskap'].sum())
    total_budget = float(df_ytd['Budsjett'].sum())
    total_avvik = float(df_ytd['Avvik'].sum())
    total_pct = (total_avvik / total_budget) if total_budget else 0

    kpis = [
        ('Regnskap YTD', total_regnskap, 'FF1B365D'),
        ('Budsjett YTD', total_budget, 'FF4A77A0'),
        ('Avvik YTD', total_avvik, 'FFC53030' if total_avvik > 0 else 'FF2563EB'),
        ('Avvik %', total_pct, 'FFC53030' if total_pct > 0 else 'FF2563EB'),
    ]

    row = 5
    for label, value, color in kpis:
        ws[f'A{row}'] = label
        ws[f'B{row}'] = value
        ws[f'A{row}'].font = Font(bold=True)
        ws[f'B{row}'].font = Font(bold=True, size=12, color=color)
        if 'Avvik %' in label:
            ws[f'B{row}'].number_format = '0.0%'
        else:
            ws[f'B{row}'].number_format = '#,##0.00 "kr"'
        row += 1

    # monthly trend table
    monthly = df.groupby('Periode', as_index=False).agg(Regnskap=('Regnskap', 'sum'), Budsjett=('Budsjett', 'sum'))
    monthly = monthly.sort_values('Periode')
    ws2 = wb.create_sheet('Data')
    ws2.append(['Periode', 'Regnskap', 'Budsjett', 'Avvik'])
    for _, r in monthly.iterrows():
        ws2.append([r['Periode'], r['Regnskap'], r['Budsjett'], r['Regnskap'] - r['Budsjett']])
    ws2.freeze_panes = 'A2'
    for cell in ws2[1]:
        cell.font = Font(bold=True, color='1B365D')
        cell.fill = PatternFill('solid', fgColor='D9EAF7')

    # summary matrix
    kpi_sheet = wb.create_sheet('KPI Matrix')
    kpi_sheet['A1'] = 'Dimensjon'
    kpi_sheet['B1'] = 'Budsjett YTD'
    kpi_sheet['C1'] = 'Regnskap YTD'
    kpi_sheet['D1'] = 'Avvik YTD'
    kpi_sheet['E1'] = 'Avvik %'
    for cell in kpi_sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill('solid', fgColor='D9EAF7')

    grouped = df_ytd.groupby('Hovedgruppe', as_index=False).agg(Budsjett=('Budsjett', 'sum'), Regnskap=('Regnskap', 'sum'), Avvik=('Avvik', 'sum'))
    for i, row in enumerate(grouped.itertuples(index=False), start=2):
        kpi_sheet[f'A{i}'] = row[0]
        kpi_sheet[f'B{i}'] = row[1]
        kpi_sheet[f'C{i}'] = row[2]
        kpi_sheet[f'D{i}'] = row[3]
        kpi_sheet[f'E{i}'] = row[3] / row[1] if row[1] else 0
    for col in ['B', 'C', 'D']:
        for cell in kpi_sheet[col]:
            if cell.row == 1:
                continue
            cell.number_format = '#,##0.00 "kr"'
    for cell in kpi_sheet['E']:
        if cell.row == 1:
            continue
        cell.number_format = '0.0%'
    kpi_sheet.auto_filter.ref = 'A1:E' + str(kpi_sheet.max_row)

    # measures sheet
    measures = wb.create_sheet('Measures')
    measures['A1'] = 'DAX Measure'
    measures['B1'] = 'Purpose'
    for cell in measures[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill('solid', fgColor='D9EAF7')
    for idx, measure in enumerate(MEASURES, start=2):
        measures[f'A{idx}'] = measure
        measures[f'B{idx}'] = {
            'Regnskap YTD': 'Akkumulert faktisk bokført regnskap YTD',
            'Budsjett YTD': 'Akkumulert periodisert budsjett YTD',
            'Avvik YTD': 'Faktisk minus budsjett',
            'Avvik YTD %': 'Prosent avvik mot budsjett',
            'Merforbruk YTD': 'Positivt avvik klassifisert som merforbruk',
            'Mindreforbruk YTD': 'Negativt avvik klassifisert som mindreforbruk',
            'Vedtatt Årsbudsjett': 'Totalt vedtatt årsramme',
            'EOY Rullende Prognose': 'Rullende prognose ved årsslutt',
            'EOY Forventet Årsavvik': 'Prognostisert avvik mot ramme',
            'Brutto Driftsresultat': 'Driftsinntekter minus driftsutgifter',
            'Brutto Driftsresultat %': 'Brutto driftsresultat som andel av inntekter',
            'Tufte_Avvik_Farge_HEX': 'Fargekode for betinget rapportformatering',
            'Planlagt Tiltakseffekt T3': 'Planlagt tiltakssum fra dokumentert scenario',
            'Framsikt Deflator Value': 'Valgt deflatorsats (standard 4,1 %)',
            'Fraværstiltak Effektreduksjon Value': 'Valgt effekt av fraværstiltak (standard 1,5 %)',
            'Simulert EOY Netto Driftsresultat': 'Simulert prognose med valgt deflator og tiltak',
            'Simulert EOY Forventet Avvik': 'Simulert årsavvik mot vedtatt ramme',
            'EOY Net Zero Sluttavvik': 'Sluttavvik etter tiltak',
        }.get(measure, 'KPI for rapportering')
        measures[f'A{idx}'].font = Font(color='1B365D')
        measures.column_dimensions['A'].width = 36
        measures.column_dimensions['B'].width = 60

    # conditional formatting on overview
    ws.conditional_formatting.add('B7:B8', CellIsRule(operator='greaterThan', formula=['0'], stopIfTrue=True, fill=PatternFill('solid', fgColor='FDE2E2')))
    ws.conditional_formatting.add('B7:B8', CellIsRule(operator='lessThan', formula=['0'], stopIfTrue=True, fill=PatternFill('solid', fgColor='E7F1FF')))

    # chart on overview after certain rows
    chart = LineChart()
    chart.title = 'Regnskap vs Budsjett - månedlig trend'
    chart.style = 12
    chart.y_axis.title = 'Beløp (kr)'
    chart.x_axis.title = 'Periode'
    data = Reference(ws2, min_col=2, min_row=1, max_col=3, max_row=ws2.max_row)
    cats = Reference(ws2, min_col=1, min_row=2, max_row=ws2.max_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 8
    chart.width = 18
    ws.add_chart(chart, 'E5')

    drivers = df_ytd.groupby(['Kontonavn', 'Hovedgruppe'], as_index=False).agg(
        Regnskap=('Regnskap', 'sum'), Budsjett=('Budsjett', 'sum'), Avvik=('Avvik', 'sum')
    )
    drivers['AbsAvvik'] = drivers['Avvik'].abs()
    drivers = drivers.sort_values('AbsAvvik', ascending=False).drop(columns='AbsAvvik')
    driver_sheet = wb.create_sheet('Drivers')
    driver_sheet.append(['Konto / post', 'Kategori', 'Regnskap YTD', 'Budsjett YTD', 'Avvik YTD'])
    for values in drivers.itertuples(index=False, name=None):
        driver_sheet.append(list(values))
    driver_sheet.freeze_panes = 'A2'
    driver_sheet.auto_filter.ref = driver_sheet.dimensions
    for cell in driver_sheet[1]:
        cell.font = Font(bold=True, color='FF1B365D')
        cell.fill = PatternFill('solid', fgColor='FFD9EAF7')
    if driver_sheet.max_row > 1:
        driver_sheet.conditional_formatting.add(
            f'E2:E{driver_sheet.max_row}',
            DataBarRule(start_type='num', start_value=0, end_type='max', color='FF95A5A6', showValue=True),
        )

    wb.save(output_path)


def build_skole_workbook(output_path: Path):
    df = pd.read_csv(DATA_DIR / 'Komskole.csv', encoding='cp1252', engine='python', header=2)
    cleaned = df.rename(columns={
        'Periode (year to date)': 'Periode',
        'Lokasjon': 'Lokasjon',
        'Art': 'Art',
        'Ansvar/Enhet': 'Ansvar_Enhet',
        'Kontotype': 'Kontotype',
        'Post': 'Post',
        'Regnskap hiå.': 'Regnskap',
        'Budsjett hiå.': 'Budsjett',
        'Avvik i kr': 'Avvik_kr',
        'Avvik i prosent': 'Avvik_pct',
        'Årsbudsjett': 'Aarsbudsjett',
        'Regnskap i fjor': 'Regnskap_fjor',
        'Kontoklasse': 'Kontoklasse',
        'Øk. Klasse': 'Ok_klasse'
    })
    cleaned = cleaned.dropna(subset=['Periode'], how='all')
    for col in ['Regnskap', 'Budsjett', 'Avvik_kr', 'Avvik_pct', 'Aarsbudsjett', 'Regnskap_fjor']:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce').fillna(0)
    cleaned['Avvik_kr'] = cleaned['Regnskap'] - cleaned['Budsjett']
    cleaned['Avvik_pct'] = cleaned.apply(
        lambda row: row['Avvik_kr'] / abs(row['Budsjett']) if row['Budsjett'] else 0,
        axis=1,
    )

    wb = Workbook()
    ws = wb.active
    ws.title = 'Overview'
    set_title(ws, 'Kommunal Skole - EPM Rapport', 'KOSTRA 202 – framsiktvisualisering og avvikssammenstilling')

    total_regnskap = float(cleaned['Regnskap'].sum())
    total_budget = float(cleaned['Budsjett'].sum())
    total_avvik = float(cleaned['Avvik_kr'].sum())
    total_pct = (total_avvik / total_budget) if total_budget else 0

    kpis = [
        ('Regnskap YTD', total_regnskap, 'FF1B365D'),
        ('Budsjett YTD', total_budget, 'FF4A77A0'),
        ('Avvik YTD', total_avvik, 'FFC53030' if total_avvik > 0 else 'FF2563EB'),
        ('Avvik %', total_pct, 'FFC53030' if total_pct > 0 else 'FF2563EB'),
    ]
    row = 5
    for label, value, color in kpis:
        ws[f'A{row}'] = label
        ws[f'B{row}'] = value
        ws[f'A{row}'].font = Font(bold=True)
        ws[f'B{row}'].font = Font(bold=True, size=12, color=color)
        if 'Avvik %' in label:
            ws[f'B{row}'].number_format = '0.0%'
        else:
            ws[f'B{row}'].number_format = '#,##0.0 "kNOK"'
        row += 1

    ws2 = wb.create_sheet('Data')
    ws2.append(['Periode', 'Lokasjon', 'Funksjon', 'Enhet', 'Regnskap (kNOK)', 'Budsjett (kNOK)', 'Avvik (kNOK)', 'Avvik %'])
    for _, row_data in cleaned[['Periode', 'Lokasjon', 'Art', 'Ansvar_Enhet', 'Regnskap', 'Budsjett', 'Avvik_kr', 'Avvik_pct']].iterrows():
        ws2.append(list(row_data))
    for cell in ws2[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill('solid', fgColor='D9EAF7')
    ws2.freeze_panes = 'A2'

    group = cleaned.groupby('Ansvar_Enhet', as_index=False).agg(Regnskap=('Regnskap', 'sum'), Budsjett=('Budsjett', 'sum'), Avvik=('Avvik_kr', 'sum'))
    matrix = wb.create_sheet('KPI Matrix')
    matrix['A1'] = 'Ansvar / enhet'
    matrix['B1'] = 'Budsjett'
    matrix['C1'] = 'Regnskap'
    matrix['D1'] = 'Avvik'
    matrix['E1'] = 'Avvik %'
    for cell in matrix[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill('solid', fgColor='D9EAF7')
    for i, row in enumerate(group.itertuples(index=False), start=2):
        matrix[f'A{i}'] = row[0]
        matrix[f'B{i}'] = row[2]
        matrix[f'C{i}'] = row[1]
        matrix[f'D{i}'] = row[3]
        matrix[f'E{i}'] = (row[3] / row[2]) if row[2] else 0
    for col in ['B', 'C', 'D']:
        for cell in matrix[col]:
            if cell.row == 1:
                continue
            cell.number_format = '#,##0.0 "kNOK"'
    for cell in matrix['E']:
        if cell.row == 1:
            continue
        cell.number_format = '0.0%'
    matrix.auto_filter.ref = 'A1:E' + str(matrix.max_row)

    measures = wb.create_sheet('Measures')
    measures['A1'] = 'DAX Measure'
    measures['B1'] = 'Purpose'
    for cell in measures[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill('solid', fgColor='D9EAF7')
    for idx, measure in enumerate(MEASURES, start=2):
        measures[f'A{idx}'] = measure
        measures[f'B{idx}'] = {
            'Regnskap YTD': 'Akkumulert faktisk regnskap YTD',
            'Budsjett YTD': 'Akkumulert periodisert budsjett YTD',
            'Avvik YTD': 'Faktisk minus budsjett',
            'Avvik YTD %': 'Prosent avvik mot budsjett',
            'Merforbruk YTD': 'Merforbruk klassifisert som positive avvik',
            'Mindreforbruk YTD': 'Mindreforbruk som positivt sparingspotensial',
            'Vedtatt Årsbudsjett': 'Totalt vedtatt årsramme',
            'EOY Rullende Prognose': 'Rullende prognose ut året',
            'EOY Forventet Årsavvik': 'Forventet årsavvik mot ramme',
            'Brutto Driftsresultat': 'Driftsresultat i hovedmengden',
            'Brutto Driftsresultat %': 'Brutto driftsresultat i prosent',
            'Tufte_Avvik_Farge_HEX': 'Fargekode for betinget rapportformatering',
            'Planlagt Tiltakseffekt T3': 'Planlagt tiltakssum fra dokumentert scenario',
            'Framsikt Deflator Value': 'Valgt deflatorsats',
            'Fraværstiltak Effektreduksjon Value': 'Valgt effektreduksjon',
            'Simulert EOY Netto Driftsresultat': 'Simulert prognose med valgte parametre',
            'Simulert EOY Forventet Avvik': 'Simulert årsavvik mot vedtatt ramme',
            'EOY Net Zero Sluttavvik': 'Tilpasset sluttavvik etter tiltak',
        }.get(measure, 'KPI for rapportering')
    measures.column_dimensions['A'].width = 38
    measures.column_dimensions['B'].width = 60

    # chart summary
    chart = BarChart()
    chart.type = 'bar'
    chart.title = 'Regnskap mot budsjett per enhet'
    chart.style = 10
    chart.x_axis.title = 'Beløp (kNOK)'
    chart.y_axis.title = 'Enhet'
    data = Reference(matrix, min_col=2, min_row=1, max_col=3, max_row=matrix.max_row)
    cats = Reference(matrix, min_col=1, min_row=2, max_row=matrix.max_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 8
    chart.width = 18
    ws.add_chart(chart, 'E5')

    drivers = cleaned.groupby(['Post', 'Kontotype'], as_index=False).agg(
        Regnskap=('Regnskap', 'sum'), Budsjett=('Budsjett', 'sum'), Avvik=('Avvik_kr', 'sum')
    )
    drivers['AbsAvvik'] = drivers['Avvik'].abs()
    drivers = drivers.sort_values('AbsAvvik', ascending=False).drop(columns='AbsAvvik')
    driver_sheet = wb.create_sheet('Drivers')
    driver_sheet.append(['Konto / post', 'Kontotype', 'Regnskap hiå (kNOK)', 'Budsjett hiå (kNOK)', 'Avvik (kNOK)'])
    for values in drivers.itertuples(index=False, name=None):
        driver_sheet.append(list(values))
    driver_sheet.freeze_panes = 'A2'
    driver_sheet.auto_filter.ref = driver_sheet.dimensions
    for cell in driver_sheet[1]:
        cell.font = Font(bold=True, color='FF1B365D')
        cell.fill = PatternFill('solid', fgColor='FFD9EAF7')
    if driver_sheet.max_row > 1:
        driver_sheet.conditional_formatting.add(
            f'E2:E{driver_sheet.max_row}',
            DataBarRule(start_type='num', start_value=0, end_type='max', color='FF95A5A6', showValue=True),
        )

    ws.conditional_formatting.add('B7:B8', CellIsRule(operator='greaterThan', formula=['0'], stopIfTrue=True, fill=PatternFill('solid', fgColor='FDE2E2')))
    ws.conditional_formatting.add('B7:B8', CellIsRule(operator='lessThan', formula=['0'], stopIfTrue=True, fill=PatternFill('solid', fgColor='E7F1FF')))

    wb.save(output_path)


def write_model_bim(target: Path, project_name: str, unit_name: str, dataset: str):
    model = {
        'name': project_name,
        'compatibilityLevel': 1600,
        'model': {
            'culture': 'nb-NO',
            'tables': [
                {
                    'name': 'Dim_Dato',
                    'columns': [
                        {'name': 'dato_key', 'dataType': 'int64'},
                        {'name': 'ar', 'dataType': 'int64'},
                        {'name': 'maned', 'dataType': 'int64'},
                        {'name': 'manedsnavn', 'dataType': 'string'},
                        {'name': 'tertial', 'dataType': 'string'},
                        {'name': 'full_dato', 'dataType': 'string'}
                    ]
                },
                {
                    'name': 'Dim_Ansvar',
                    'columns': [
                        {'name': 'ansvar_kode', 'dataType': 'string'},
                        {'name': 'ansvar_navn', 'dataType': 'string'},
                        {'name': 'kommunalsjefomrade', 'dataType': 'string'},
                        {'name': 'leder_epost', 'dataType': 'string'}
                    ]
                },
                {
                    'name': 'Dim_Funksjon',
                    'columns': [
                        {'name': 'funksjon_kode', 'dataType': 'string'},
                        {'name': 'funksjon_navn', 'dataType': 'string'},
                        {'name': 'sektor', 'dataType': 'string'}
                    ]
                },
                {
                    'name': 'Fact_Regnskap',
                    'columns': [
                        {'name': 'transaksjon_id', 'dataType': 'string'},
                        {'name': 'dato_key', 'dataType': 'int64'},
                        {'name': 'funksjon_kode', 'dataType': 'string'},
                        {'name': 'ansvar_kode', 'dataType': 'string'},
                        {'name': 'KOSTRA_Art', 'dataType': 'string'},
                        {'name': 'Kontokode', 'dataType': 'string'},
                        {'name': 'Kontonavn', 'dataType': 'string'},
                        {'name': 'Budsjett', 'dataType': 'double'},
                        {'name': 'Regnskap', 'dataType': 'double'},
                        {'name': 'Avvik', 'dataType': 'double'},
                        {'name': 'Merforbruk', 'dataType': 'double'}
                    ]
                }
            ],
            'relationships': [
                {'fromTable': 'Fact_Regnskap', 'fromColumn': 'dato_key', 'toTable': 'Dim_Dato', 'toColumn': 'dato_key', 'cardinality': 'many', 'isOneToMany': True},
                {'fromTable': 'Fact_Regnskap', 'fromColumn': 'funksjon_kode', 'toTable': 'Dim_Funksjon', 'toColumn': 'funksjon_kode', 'cardinality': 'many', 'isOneToMany': True},
                {'fromTable': 'Fact_Regnskap', 'fromColumn': 'ansvar_kode', 'toTable': 'Dim_Ansvar', 'toColumn': 'ansvar_kode', 'cardinality': 'many', 'isOneToMany': True}
            ],
            'measures': [
                {'name': 'Regnskap YTD', 'expression': 'CALCULATE(SUM(Fact_Regnskap[Regnskap]), Dim_Dato[maned] <= 8)'},
                {'name': 'Budsjett YTD', 'expression': 'CALCULATE(SUM(Fact_Regnskap[Budsjett]), Dim_Dato[maned] <= 8)'},
                {'name': 'Avvik YTD', 'expression': '[Regnskap YTD] - [Budsjett YTD]'},
                {'name': 'Avvik YTD %', 'expression': 'DIVIDE([Avvik YTD], [Budsjett YTD], 0)'},
                {'name': 'Merforbruk YTD', 'expression': 'IF([Avvik YTD] > 0, [Avvik YTD], 0)'},
                {'name': 'Mindreforbruk YTD', 'expression': 'IF([Avvik YTD] < 0, ABS([Avvik YTD]), 0)'},
                {'name': 'EOY Rullende Prognose', 'expression': '[Regnskap YTD] + CALCULATE(SUM(Fact_Regnskap[Budsjett]), Dim_Dato[maned] > 8) + IF([Avvik YTD] > 0, [Avvik YTD] * 0.5, 0)'},
                {'name': 'EOY Forventet Årsavvik', 'expression': '[EOY Rullende Prognose] - CALCULATE(SUM(Fact_Regnskap[Budsjett]), ALL(Dim_Dato))'},
                {'name': 'Brutto Driftsresultat', 'expression': 'VAR Driftsinntekter = CALCULATE([Regnskap YTD], Fact_Regnskap[Hovedgruppe] = "3 Inntekter") RETURN Driftsinntekter - CALCULATE([Regnskap YTD], Fact_Regnskap[Hovedgruppe] IN {"1 Lønn", "2 Utgifter"})'},
                {'name': 'Brutto Driftsresultat %', 'expression': 'VAR TotaleInntekter = CALCULATE([Regnskap YTD], Fact_Regnskap[Hovedgruppe] = "3 Inntekter") RETURN DIVIDE([Brutto Driftsresultat], ABS(TotaleInntekter), 0)'},
                {'name': 'Tufte_Avvik_Farge_HEX', 'expression': 'VAR Avvik = [Avvik YTD] RETURN SWITCH(TRUE(), Avvik > 50000, "#DC2626", Avvik > 0, "#D97706", "#2563EB")'},
                {'name': 'EOY Net Zero Sluttavvik', 'expression': 'VAR Baseline = [Regnskap YTD] + ([Regnskap YTD]/8)*4 RETURN Baseline - CALCULATE(SUM(Fact_Regnskap[Budsjett]), ALL(Dim_Dato))'}
            ]
        }
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(model, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_pbip(project_root: Path, project_name: str, report_name: str, semantic_model_name: str):
    pbip_path = project_root / f'{project_name}.pbip'
    pbip_path.write_text(json.dumps({
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json',
        'version': '1.0',
        'artifacts': [
            {'report': {'path': report_name}}
        ],
        'settings': {'enableAutoRecovery': True}
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    report_dir = project_root / report_name
    report_dir.mkdir(parents=True, exist_ok=True)
    report_def = report_dir / 'definition'
    report_def.mkdir(parents=True, exist_ok=True)
    (report_def / 'pages').mkdir(exist_ok=True)
    (report_dir / 'definition.pbir').write_text(json.dumps({
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json',
        'version': '4.0',
        'datasetReference': {'byPath': {'path': f'../{semantic_model_name}'}}
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    page = {
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',
        'name': 'default-report-page',
        'displayName': 'KPI-oversikt',
        'displayOption': 'FitToPage',
        'height': 1080,
        'width': 1920,
        'visualContainers': []
    }
    (report_def / 'pages' / 'default-report-page.json').write_text(json.dumps(page, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (report_def / 'pages' / 'pages.json').write_text(json.dumps({
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json',
        'pageOrder': ['default-report-page'],
        'activePageName': 'default-report-page'
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    if not (report_def / 'report.json').exists():
        (report_def / 'report.json').write_text(json.dumps({
            '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json',
            'themeCollection': {'baseTheme': {'name': 'Fluent2-CY26SU09', 'reportVersionAtImport': {'visual': '2.13.0', 'report': '3.4.0', 'page': '2.3.1'}, 'type': 'SharedResources'}},
            'objects': {'section': [{'properties': {'verticalAlignment': {'expr': {'Literal': {'Value': "'Top'"}}}}}]},
            'resourcePackages': [{'name': 'SharedResources', 'type': 'SharedResources', 'items': [{'name': 'Fluent2-CY26SU09', 'path': 'BaseThemes/Fluent2-CY26SU09.json', 'type': 'BaseTheme'}]}],
            'settings': {'useStylableVisualContainerHeader': True, 'exportDataMode': 'AllowSummarized', 'defaultDrillFilterOtherVisuals': True, 'allowChangeFilterTypes': True, 'useEnhancedTooltips': True, 'useDefaultAggregateDisplayName': True}
        }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    semantic_model_dir = project_root / semantic_model_name
    semantic_model_dir.mkdir(parents=True, exist_ok=True)
    (semantic_model_dir / 'definition.pbism').write_text(json.dumps({
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json',
        'version': '4.2',
        'settings': {}
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_tmdl_model(semantic_model_dir, project_name, 'BoMiljø.csv' if 'Bo og Miljø' in project_name else 'Komskole.csv')
    write_pbir_pages(project_root, report_name, 'school' if 'Skole' in project_name else 'bomiljo')


def write_tmdl_model(model_dir: Path, model_name: str, csv_name: str):
    definition = model_dir / 'definition'
    tables_dir = definition / 'tables'
    tables_dir.mkdir(parents=True, exist_ok=True)
    (definition / 'model.tmdl').write_text(
        'model Model\n'
        '\tculture: nb-NO\n'
        '\tdefaultPowerBIDataSourceVersion: powerBI_V3\n'
        '\tsourceQueryCulture: en-US\n'
        '\tvalueFilterBehavior: independent\n'
        '\n'
        '\tref table Fact_Regnskap\n'
        '\tref table Dim_Dato\n'
        '\tref table Dim_Ansvar\n'
        '\tref table Dim_Funksjon\n'
        '\tref table Dim_Art\n'
        '\tref table Framsikt_Deflator\n'
        '\tref table Fravaer_Reduksjon\n'
        '\tref table Audit_AI_Actions\n'
        '\tref table _Measures\n'
        '\tref relationship FactDate\n'
        '\tref relationship FactAnsvar\n'
        '\tref relationship FactFunksjon\n'
        '\tref relationship FactArt\n'
        '\tref role Enhetsleder_Skole\n'
        '\tref role Enhetsleder_Boenhet\n'
        '\tref role Kommunalsjef_Oppvekst\n'
        '\tref role Kommunalsjef_Helse\n'
        '\tref role Konsern_Okonomi\n'
        '\tref expression DataRoot\n',
        encoding='utf-8',
    )
    (definition / 'expressions.tmdl').write_text(
        'expression DataRoot = "C:\\CHANGE_ME\\use cases\\data\\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n',
        encoding='utf-8',
    )
    (definition / 'roles.tmdl').write_text(
        'role Enhetsleder_Skole\n'
        '\tmodelPermission: read\n'
        '\ttablePermission Dim_Ansvar\n'
        '\t\tfilterExpression: [ansvar_kode] = "2020"\n'
        '\n'
        'role Enhetsleder_Boenhet\n'
        '\tmodelPermission: read\n'
        '\ttablePermission Dim_Ansvar\n'
        '\t\tfilterExpression: [ansvar_kode] = "2540"\n'
        '\n'
        'role Kommunalsjef_Oppvekst\n'
        '\tmodelPermission: read\n'
        '\ttablePermission Dim_Ansvar\n'
        '\t\tfilterExpression: [kommunalsjefomrade] = "Oppvekst"\n'
        '\n'
        'role Kommunalsjef_Helse\n'
        '\tmodelPermission: read\n'
        '\ttablePermission Dim_Ansvar\n'
        '\t\tfilterExpression: [kommunalsjefomrade] = "Helse og mestring"\n'
        '\n'
        'role Konsern_Okonomi\n'
        '\tmodelPermission: read\n',
        encoding='utf-8',
    )
    (definition / 'relationships.tmdl').write_text(
        'relationship FactDate\n'
        '\tfromColumn: Fact_Regnskap.dato\n'
        '\ttoColumn: Dim_Dato.dato\n'
        '\tfromCardinality: many\n'
        '\ttoCardinality: one\n'
        '\tcrossFilteringBehavior: oneDirection\n'
        '\n'
        'relationship FactAnsvar\n'
        '\tfromColumn: Fact_Regnskap.ansvar_kode\n'
        '\ttoColumn: Dim_Ansvar.ansvar_kode\n'
        '\tfromCardinality: many\n'
        '\ttoCardinality: one\n'
        '\tcrossFilteringBehavior: oneDirection\n'
        '\n'
        'relationship FactFunksjon\n'
        '\tfromColumn: Fact_Regnskap.funksjon_kode\n'
        '\ttoColumn: Dim_Funksjon.funksjon_kode\n'
        '\tfromCardinality: many\n'
        '\ttoCardinality: one\n'
        '\tcrossFilteringBehavior: oneDirection\n'
        '\n'
        'relationship FactArt\n'
        '\tfromColumn: Fact_Regnskap.art_key\n'
        '\ttoColumn: Dim_Art.art_key\n'
        '\tfromCardinality: many\n'
        '\ttoCardinality: one\n'
        '\tcrossFilteringBehavior: oneDirection\n'
        '\n'
        'relationship AuditResponsibility\n'
        '\tfromColumn: Audit_AI_Actions.ansvar_kode\n'
        '\ttoColumn: Dim_Ansvar.ansvar_kode\n'
        '\tfromCardinality: many\n'
        '\ttoCardinality: one\n'
        '\tcrossFilteringBehavior: oneDirection\n',
        encoding='utf-8',
    )

    if csv_name == 'BoMiljø.csv':
        source = '''let
    Source = Csv.Document(File.Contents(DataRoot & "BoMiljø.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"Måned_Nr", Int64.Type}, {"KOSTRA_Funksjon", type text}, {"Tjenesteområde", type text}, {"KOSTRA_Art", type text}, {"Kontokode", type text}, {"Budsjett", type number}, {"Regnskap", type number}, {"Avvik", type number}, {"Merforbruk", type number}}, "en-US"),
    AddDate = Table.AddColumn(Typed, "dato", each Date.FromText([Periode] & "-01"), type date),
    AddResponsibility = Table.AddColumn(AddDate, "ansvar_kode", each "2540", type text),
    AddResponsibilityName = Table.AddColumn(AddResponsibility, "ansvar_navn", each [Lokasjon], type text),
    AddFunction = Table.AddColumn(AddResponsibilityName, "funksjon_kode", each Text.From([KOSTRA_Funksjon]), type text),
    AddSector = Table.AddColumn(AddFunction, "kommunalsjefomrade", each [Tjenesteområde], type text),
    AddArtKey = Table.AddColumn(AddSector, "art_key", each Text.From([KOSTRA_Art]) & "|" & Text.From([Kontokode]) & "|" & Text.From([Kontonavn]), type text),
    AddAnnualBudget = Table.AddColumn(AddArtKey, "Aarsbudsjett", each [Budsjett], type number),
    Rename = Table.RenameColumns(AddAnnualBudget, {{"Måned_Nr", "maned"}, {"Måned", "manedsnavn"}}),
    Keep = Table.SelectColumns(Rename, {"dato", "maned", "manedsnavn", "Tertial", "Status", "ansvar_kode", "ansvar_navn", "kommunalsjefomrade", "funksjon_kode", "art_key", "Hovedgruppe", "Undergruppe", "KOSTRA_Art", "Kontokode", "Kontonavn", "Budsjett", "Regnskap", "Avvik", "Merforbruk", "Aarsbudsjett"})
in
    Keep'''
        model_tables = {
            'Fact_Regnskap': [
                ('dato', 'dateTime'), ('maned', 'int64'), ('manedsnavn', 'string'), ('Tertial', 'string'), ('Status', 'string'),
                ('ansvar_kode', 'string'), ('ansvar_navn', 'string'), ('kommunalsjefomrade', 'string'), ('funksjon_kode', 'string'), ('art_key', 'string'),
                ('Hovedgruppe', 'string'), ('Undergruppe', 'string'), ('KOSTRA_Art', 'string'), ('Kontokode', 'string'),
                ('Kontonavn', 'string'), ('Budsjett', 'double'), ('Regnskap', 'double'), ('Avvik', 'double'),
                ('Merforbruk', 'double'), ('Aarsbudsjett', 'double'),
            ],
            'Dim_Dato': [('dato', 'dateTime'), ('ar', 'int64'), ('maned', 'int64'), ('manedsnavn', 'string'), ('tertial', 'string')],
            'Dim_Ansvar': [('ansvar_kode', 'string'), ('ansvar_navn', 'string'), ('kommunalsjefomrade', 'string')],
            'Dim_Funksjon': [('funksjon_kode', 'string')],
            'Dim_Art': [('art_key', 'string'), ('KOSTRA_Art', 'string'), ('Kontokode', 'string'), ('Kontonavn', 'string'), ('Hovedgruppe', 'string'), ('Undergruppe', 'string')],
        }
    else:
        source = '''let
    Source = Csv.Document(File.Contents(DataRoot & "Komskole.csv"), [Delimiter=",", Encoding=1252, QuoteStyle=QuoteStyle.Csv]),
    DataRows = Table.Skip(Source, 2),
    Headers = Table.PromoteHeaders(DataRows, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"Art", type text}, {"Regnskap hiå.", type number}, {"Budsjett hiå.", type number}, {"Avvik i kr", type number}, {"Årsbudsjett", type number}, {"Regnskap i fjor", type number}}, "en-US"),
    AddDate = Table.AddColumn(Typed, "dato", each #date(2000 + Number.FromText(Text.End([#"Periode (year to date)"], 2)), 8, 1), type date),
    AddResponsibility = Table.AddColumn(AddDate, "ansvar_kode", each "2020", type text),
    AddResponsibilityName = Table.AddColumn(AddResponsibility, "ansvar_navn", each [#"Ansvar/Enhet"], type text),
    AddFunction = Table.AddColumn(AddResponsibilityName, "funksjon_kode", each Text.From([Art]), type text),
    AddDateMonth = Table.AddColumn(AddFunction, "maned", each Date.Month([dato]), Int64.Type),
    AddMonthName = Table.AddColumn(AddDateMonth, "manedsnavn", each Date.ToText([dato], "MMMM", "nb-NO"), type text),
    AddTertial = Table.AddColumn(AddMonthName, "Tertial", each "T2", type text),
    AddStatus = Table.AddColumn(AddTertial, "Status", each "Bokført", type text),
    AddCategory = Table.AddColumn(AddStatus, "Hovedgruppe", each [Kontotype], type text),
    AddSubcategory = Table.AddColumn(AddCategory, "Undergruppe", each [Kontotype], type text),
    AddArtKey = Table.AddColumn(AddSubcategory, "art_key", each Text.From([Art]) & "|" & Text.From([Kontotype]) & "|" & Text.From([Post]), type text),
    AddAccountCode = Table.AddColumn(AddArtKey, "KOSTRA_Art", each null, type text),
    AddBudget = Table.AddColumn(AddAccountCode, "Budsjett", each [#"Budsjett hiå."], type number),
    AddActual = Table.AddColumn(AddBudget, "Regnskap", each [#"Regnskap hiå."], type number),
    AddVariance = Table.AddColumn(AddActual, "Avvik", each [#"Regnskap hiå."] - [#"Budsjett hiå."], type number),
    AddOverrun = Table.AddColumn(AddVariance, "Merforbruk", each [Avvik], type number),
    AddSector = Table.AddColumn(AddOverrun, "kommunalsjefomrade", each "Oppvekst", type text),
    Rename = Table.RenameColumns(AddSector, {{"Post", "Kontonavn"}, {"Kontotype", "Kontokode"}, {"Årsbudsjett", "Aarsbudsjett"}}),
    Keep = Table.SelectColumns(Rename, {"dato", "maned", "manedsnavn", "Tertial", "Status", "ansvar_kode", "ansvar_navn", "kommunalsjefomrade", "funksjon_kode", "art_key", "Hovedgruppe", "Undergruppe", "KOSTRA_Art", "Kontokode", "Kontonavn", "Budsjett", "Regnskap", "Avvik", "Merforbruk", "Aarsbudsjett"})
in
    Keep'''
        model_tables = {
            'Fact_Regnskap': [
                ('dato', 'dateTime'), ('maned', 'int64'), ('manedsnavn', 'string'), ('Tertial', 'string'), ('Status', 'string'),
                ('ansvar_kode', 'string'), ('ansvar_navn', 'string'), ('kommunalsjefomrade', 'string'), ('funksjon_kode', 'string'), ('art_key', 'string'),
                ('Hovedgruppe', 'string'), ('Undergruppe', 'string'), ('KOSTRA_Art', 'string'), ('Kontokode', 'string'),
                ('Kontonavn', 'string'), ('Budsjett', 'double'), ('Regnskap', 'double'), ('Avvik', 'double'),
                ('Merforbruk', 'double'), ('Aarsbudsjett', 'double'),
            ],
            'Dim_Dato': [('dato', 'dateTime'), ('ar', 'int64'), ('maned', 'int64'), ('manedsnavn', 'string'), ('tertial', 'string')],
            'Dim_Ansvar': [('ansvar_kode', 'string'), ('ansvar_navn', 'string'), ('kommunalsjefomrade', 'string')],
            'Dim_Funksjon': [('funksjon_kode', 'string')],
            'Dim_Art': [('art_key', 'string'), ('KOSTRA_Art', 'string'), ('Kontokode', 'string'), ('Kontonavn', 'string'), ('Hovedgruppe', 'string'), ('Undergruppe', 'string')],
        }

    model_tables['Framsikt_Deflator'] = [('Value', 'double'), ('Label', 'string')]
    model_tables['Fravaer_Reduksjon'] = [('Value', 'double'), ('Label', 'string')]
    model_tables['Audit_AI_Actions'] = [
        ('Tidsstempel', 'dateTime'), ('Enhetskode', 'string'), ('ansvar_kode', 'string'),
        ('AI_Tiltak', 'string'), ('Konfidens', 'double'), ('Leder_Beslutning', 'string'),
        ('Saksbehandler', 'string'), ('Begrunnelse', 'string'),
    ]

    dax = {
        'Regnskap YTD': 'CALCULATE(SUM(Fact_Regnskap[Regnskap]), Dim_Dato[maned] <= 8)',
        'Budsjett YTD': 'CALCULATE(SUM(Fact_Regnskap[Budsjett]), Dim_Dato[maned] <= 8)',
        'Avvik YTD': '[Regnskap YTD] - [Budsjett YTD]',
        'Avvik YTD %': 'DIVIDE([Avvik YTD], ABS([Budsjett YTD]), 0)',
        'Merforbruk YTD': 'MAX([Avvik YTD], 0)',
        'Mindreforbruk YTD': 'MAX(-[Avvik YTD], 0)',
        'Vedtatt Årsbudsjett': 'CALCULATE(SUM(Fact_Regnskap[Aarsbudsjett]), REMOVEFILTERS(Dim_Dato))',
        'EOY Rullende Prognose': 'VAR AnnualBudget = [Vedtatt Årsbudsjett] VAR RemainingBudget = MAX(AnnualBudget - [Budsjett YTD], 0) RETURN [Regnskap YTD] + RemainingBudget + MAX([Avvik YTD], 0) * 0.5',
        'EOY Forventet Årsavvik': '[EOY Rullende Prognose] - [Vedtatt Årsbudsjett]',
        'Brutto Driftsresultat': 'CALCULATE([Regnskap YTD], Fact_Regnskap[Hovedgruppe] = "3 Inntekter") - CALCULATE([Regnskap YTD], Fact_Regnskap[Hovedgruppe] IN {"1 Lønn", "2 Utgifter"})',
        'Brutto Driftsresultat %': 'DIVIDE([Brutto Driftsresultat], ABS(CALCULATE([Regnskap YTD], Fact_Regnskap[Hovedgruppe] = "3 Inntekter")), 0)',
        'Tufte_Avvik_Farge_HEX': 'SWITCH(TRUE(), [Avvik YTD %] > 0.02, "#C53030", [Avvik YTD %] > 0, "#D69E2E", "#2F855A")',
        'EOY Net Zero Sluttavvik': '[EOY Forventet Årsavvik] - [Planlagt Tiltakseffekt T3]',
        'Planlagt Tiltakseffekt T3': 'SWITCH(SELECTEDVALUE(Dim_Ansvar[ansvar_kode]), "2540", 1928421, "2020", 863000, 2791421)',
        'Framsikt Deflator Value': 'SELECTEDVALUE(Framsikt_Deflator[Value], 0.041)',
        'Fraværstiltak Effektreduksjon Value': 'SELECTEDVALUE(Fravaer_Reduksjon[Value], 0.015)',
        'Simulert EOY Netto Driftsresultat': 'VAR DeflatorAddition = [Vedtatt Årsbudsjett] * [Framsikt Deflator Value] VAR VikarBase = CALCULATE(SUM(Fact_Regnskap[Regnskap]), Fact_Regnskap[KOSTRA_Art] = "1020") VAR VikarSavings = VikarBase * [Fraværstiltak Effektreduksjon Value] RETURN [EOY Rullende Prognose] + DeflatorAddition + VikarSavings',
        'Simulert EOY Forventet Avvik': '[Simulert EOY Netto Driftsresultat] - [Vedtatt Årsbudsjett]',
    }
    for table_name, columns in model_tables.items():
        if table_name == 'Fact_Regnskap':
            m_source = source
        elif table_name == 'Dim_Dato':
            m_source = 'let Source = Fact_Regnskap, Selected = Table.SelectColumns(Source, {"dato", "Tertial"}), Rename = Table.RenameColumns(Selected, {{"Tertial", "tertial"}}), Unique = Table.Distinct(Rename), AddYear = Table.AddColumn(Unique, "ar", each Date.Year([dato]), Int64.Type), AddMonth = Table.AddColumn(AddYear, "maned", each Date.Month([dato]), Int64.Type), AddName = Table.AddColumn(AddMonth, "manedsnavn", each Date.ToText([dato], "MMMM", "nb-NO"), type text) in AddName'
        elif table_name == 'Dim_Ansvar':
            m_source = 'let Source = Fact_Regnskap, Selected = Table.SelectColumns(Source, {"ansvar_kode", "ansvar_navn", "kommunalsjefomrade"}), Unique = Table.Distinct(Selected) in Unique'
        elif table_name == 'Dim_Funksjon':
            m_source = 'let Source = Fact_Regnskap, Selected = Table.SelectColumns(Source, {"funksjon_kode"}), Unique = Table.Distinct(Selected) in Unique'
        elif table_name == 'Dim_Art':
            m_source = 'let Source = Fact_Regnskap, Selected = Table.SelectColumns(Source, {"art_key", "KOSTRA_Art", "Kontokode", "Kontonavn", "Hovedgruppe", "Undergruppe"}), Unique = Table.Distinct(Selected) in Unique'
        elif table_name == 'Audit_AI_Actions':
            m_source = 'let Source = #table(type table [Tidsstempel = datetime, Enhetskode = text, ansvar_kode = text, AI_Tiltak = text, Konfidens = number, Leder_Beslutning = text, Saksbehandler = text, Begrunnelse = text], {}) in Source'
        elif table_name == 'Framsikt_Deflator':
            m_source = 'let Values = List.Transform({20..60}, each Number.From(_) / 1000), Source = Table.FromList(Values, Splitter.SplitByNothing(), {"Value"}), AddLabel = Table.AddColumn(Source, "Label", each Number.ToText([Value], "0.0%"), type text) in AddLabel'
        else:
            m_source = 'let Values = List.Transform({0..30}, each Number.From(_) / 1000), Source = Table.FromList(Values, Splitter.SplitByNothing(), {"Value"}), AddLabel = Table.AddColumn(Source, "Label", each Number.ToText([Value], "0.0%"), type text) in AddLabel'

        lines = [f'table {table_name}', '']
        for column_name, data_type in columns:
            lines.extend([
                f'\tcolumn {column_name}',
                f'\t\tdataType: {data_type}',
                '\t\tsummarizeBy: none' if data_type == 'string' or column_name in {'dato', 'maned', 'ar'} else '\t\tsummarizeBy: sum',
                f'\t\tsourceColumn: {column_name}',
                '',
            ])
            if table_name == 'Dim_Dato' and column_name == 'manedsnavn':
                lines[-1:-1] = ['\t\tsortByColumn: maned']
        lines.extend([
            f'\tpartition {table_name} = m',
            '\t\tmode: import',
            '\t\tsource =',
            *[f'\t\t\t\t{line}' for line in m_source.splitlines()],
            '',
            '\tannotation PBI_ResultType = Table',
            '',
        ])
        (tables_dir / f'{table_name}.tmdl').write_text('\n'.join(lines), encoding='utf-8')

    measure_lines = ['table _Measures', '', '\tcolumn Placeholder', '\t\tdataType: int64', '\t\tisHidden', '\t\tsummarizeBy: none', '\t\tsourceColumn: Placeholder', '']
    measure_lines.extend([
        '\tpartition _Measures = m',
        '\t\tmode: import',
        '\t\tsource = #table(type table [Placeholder = Int64.Type], {{1}})',
        '',
    ])
    for name, expression in dax.items():
        measure_lines.extend([f'\tmeasure \'{name}\' = {expression}', ''])
        if name != 'Tufte_Avvik_Farge_HEX':
            format_string = (
                '0.0%'
                if name.endswith('%') or name in {'Framsikt Deflator Value', 'Fraværstiltak Effektreduksjon Value'}
                else '#,##0.0 "kNOK"'
                if csv_name == 'Komskole.csv'
                else '#,##0.00 "kr"'
            )
            measure_lines[-1:-1] = [f'\t\tformatString: {format_string}']
    (tables_dir / '_Measures.tmdl').write_text('\n'.join(measure_lines), encoding='utf-8')
    (model_dir / 'model.bim').unlink(missing_ok=True)


def _pbir_projection(table, field, kind='Column'):
    return {
        'field': {kind: {'Expression': {'SourceRef': {'Entity': table}}, 'Property': field}},
        'queryRef': f'{table}.{field}',
        'nativeQueryRef': field,
        'active': True,
    }


def _pbir_visual(page_dir, visual_type, fields_by_role, position, title=None):
    visual_name = uuid.uuid4().hex[:20]
    visual_dir = page_dir / 'visuals' / visual_name
    visual_dir.mkdir(parents=True, exist_ok=True)
    query_state = {
        role: {'projections': [
            _pbir_projection(table, field, kind)
            for table, field, kind in field_specs
        ]}
        for role, field_specs in fields_by_role.items()
    }
    visual = {
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.3.0/schema.json',
        'name': visual_name,
        'position': position,
        'visual': {
            'visualType': visual_type,
            'drillFilterOtherVisuals': True,
            'query': {'queryState': query_state},
        },
    }
    if title:
        visual['visual']['visualContainerObjects'] = {
            'title': [{'properties': {'show': {'expr': {'Literal': {'Value': 'true'}}}, 'text': {'expr': {'Literal': {'Value': f"'{title}'"}}}}}]
        }
    (visual_dir / 'visual.json').write_text(json.dumps(visual, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return visual_name


def write_pbir_pages(project_root: Path, report_name: str, unit: str):
    report_def = project_root / report_name / 'definition'
    pages_dir = report_def / 'pages'
    pages_dir.mkdir(parents=True, exist_ok=True)
    page_specs = [
        ('overview', 'Resultatoversikt'),
        ('drivers', 'Avviksdrivere'),
        ('outlook', 'Prognose og tiltak'),
        ('audit', 'Ansvarlig AI og audit trail'),
    ]
    generated_names = {display_name for _, display_name in page_specs}
    for existing in pages_dir.iterdir():
        page_file = existing / 'page.json' if existing.is_dir() else None
        if page_file and page_file.exists():
            existing_page = json.loads(page_file.read_text(encoding='utf-8'))
            if existing_page.get('displayName') in generated_names:
                shutil.rmtree(existing)
    (pages_dir / 'default-report-page.json').unlink(missing_ok=True)
    page_order = []
    for page_key, display_name in page_specs:
        page_id = uuid.uuid5(uuid.NAMESPACE_URL, f'{report_name}:{page_key}').hex[:20]
        page_order.append(page_id)
        page_dir = pages_dir / page_id
        page_dir.mkdir(parents=True, exist_ok=True)
        page = {
            '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',
            'name': page_id,
            'displayName': display_name,
            'displayOption': 'FitToPage',
            'height': 900,
            'width': 1600,
        }
        (page_dir / 'page.json').write_text(json.dumps(page, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if page_key == 'overview':
            measures = [
                ('Regnskap YTD', 0, 0),
                ('Budsjett YTD', 400, 0),
                ('Avvik YTD', 800, 0),
                ('EOY Forventet Årsavvik', 1200, 0),
            ]
            for measure, x, y in measures:
                _pbir_visual(page_dir, 'card', {'Values': [('_Measures', measure, 'Measure')]},
                             {'x': x, 'y': y, 'z': x // 100 + 1, 'width': 380, 'height': 155, 'tabOrder': x // 100},
                             measure)
            _pbir_visual(page_dir, 'tableEx', {
                'Values': [
                    ('Dim_Ansvar', 'kommunalsjefomrade', 'Column'),
                    ('Dim_Ansvar', 'ansvar_navn', 'Column'),
                    ('_Measures', 'Budsjett YTD', 'Measure'),
                    ('_Measures', 'Regnskap YTD', 'Measure'),
                    ('_Measures', 'Avvik YTD', 'Measure'),
                    ('_Measures', 'Avvik YTD %', 'Measure'),
                    ('_Measures', 'EOY Forventet Årsavvik', 'Measure'),
                ]
            }, {'x': 0, 'y': 180, 'z': 5, 'width': 1570, 'height': 670, 'tabOrder': 5}, 'Sektor- og enhetsmatrise')
            _pbir_visual(page_dir, 'slicer', {'Values': [('Dim_Dato', 'ar', 'Column')]},
                         {'x': 0, 'y': 850, 'z': 6, 'width': 300, 'height': 45, 'tabOrder': 6}, 'År')
        elif page_key == 'drivers':
            if unit == 'bomiljo':
                _pbir_visual(page_dir, 'decompositionTree', {
                    'Analyze': [('_Measures', 'Avvik YTD', 'Measure')],
                    'ExplainBy': [
                        ('Dim_Ansvar', 'kommunalsjefomrade', 'Column'),
                        ('Dim_Funksjon', 'funksjon_kode', 'Column'),
                        ('Dim_Ansvar', 'ansvar_navn', 'Column'),
                        ('Dim_Art', 'KOSTRA_Art', 'Column'),
                    ],
                }, {'x': 0, 'y': 0, 'z': 1, 'width': 920, 'height': 820, 'tabOrder': 1}, 'Dekomponering av YTD-avvik')
            else:
                _pbir_visual(page_dir, 'columnChart', {
                    'Category': [('Dim_Art', 'Kontonavn', 'Column')],
                    'Y': [('_Measures', 'Avvik YTD', 'Measure')],
                }, {'x': 0, 'y': 0, 'z': 1, 'width': 1000, 'height': 700, 'tabOrder': 1}, 'Avvik per konto / post')
            _pbir_visual(page_dir, 'tableEx', {
                'Values': [
                    ('Dim_Art', 'Kontonavn', 'Column'),
                    ('Dim_Art', 'Hovedgruppe', 'Column'),
                    ('_Measures', 'Regnskap YTD', 'Measure'),
                    ('_Measures', 'Budsjett YTD', 'Measure'),
                    ('_Measures', 'Avvik YTD', 'Measure'),
                ]
            }, {'x': 950 if unit == 'bomiljo' else 0, 'y': 0 if unit == 'bomiljo' else 710, 'z': 2, 'width': 620, 'height': 700 if unit == 'bomiljo' else 180, 'tabOrder': 2}, 'Kontodrivere')
        elif page_key == 'outlook':
            if unit == 'bomiljo':
                _pbir_visual(page_dir, 'lineChart', {
                    'Category': [('Dim_Dato', 'manedsnavn', 'Column')],
                    'Y': [('_Measures', 'Regnskap YTD', 'Measure'), ('_Measures', 'Budsjett YTD', 'Measure')],
                    'Series': [('Dim_Dato', 'ar', 'Column')],
                }, {'x': 0, 'y': 0, 'z': 1, 'width': 1050, 'height': 650, 'tabOrder': 1}, 'Regnskap og budsjett over tid')
            else:
                _pbir_visual(page_dir, 'tableEx', {
                    'Values': [
                        ('Dim_Dato', 'dato', 'Column'),
                        ('_Measures', 'Regnskap YTD', 'Measure'),
                        ('_Measures', 'Budsjett YTD', 'Measure'),
                        ('_Measures', 'Avvik YTD', 'Measure'),
                    ]
                }, {'x': 0, 'y': 0, 'z': 1, 'width': 800, 'height': 300, 'tabOrder': 1}, 'Kildeperioden er ett YTD-snapshot')
            _pbir_visual(page_dir, 'card', {'Values': [('_Measures', 'EOY Net Zero Sluttavvik', 'Measure')]},
                         {'x': 1100, 'y': 0, 'z': 2, 'width': 450, 'height': 210, 'tabOrder': 2}, 'Balansert sluttavvik')
            _pbir_visual(page_dir, 'card', {'Values': [('_Measures', 'Planlagt Tiltakseffekt T3', 'Measure')]},
                         {'x': 1100, 'y': 250, 'z': 3, 'width': 450, 'height': 210, 'tabOrder': 3}, 'Planlagt tiltakseffekt T3')
            _pbir_visual(page_dir, 'card', {'Values': [('_Measures', 'Simulert EOY Netto Driftsresultat', 'Measure')]},
                         {'x': 1100, 'y': 490, 'z': 4, 'width': 450, 'height': 180, 'tabOrder': 4}, 'Simulert årsresultat')
            _pbir_visual(page_dir, 'card', {'Values': [('_Measures', 'Simulert EOY Forventet Avvik', 'Measure')]},
                         {'x': 1100, 'y': 690, 'z': 5, 'width': 450, 'height': 180, 'tabOrder': 5}, 'Simulert årsavvik')
            _pbir_visual(page_dir, 'slicer', {'Values': [('Framsikt_Deflator', 'Label', 'Column')]},
                         {'x': 0, 'y': 700, 'z': 6, 'width': 500, 'height': 150, 'tabOrder': 6}, 'Framsikt Deflator %')
            _pbir_visual(page_dir, 'slicer', {'Values': [('Fravaer_Reduksjon', 'Label', 'Column')]},
                         {'x': 520, 'y': 700, 'z': 7, 'width': 500, 'height': 150, 'tabOrder': 7}, 'Fraværstiltak Reduksjon %')
        else:
            _pbir_visual(page_dir, 'tableEx', {
                'Values': [
                    ('Audit_AI_Actions', 'Tidsstempel', 'Column'),
                    ('Audit_AI_Actions', 'Enhetskode', 'Column'),
                    ('Audit_AI_Actions', 'AI_Tiltak', 'Column'),
                    ('Audit_AI_Actions', 'Konfidens', 'Column'),
                    ('Audit_AI_Actions', 'Leder_Beslutning', 'Column'),
                    ('Audit_AI_Actions', 'Saksbehandler', 'Column'),
                    ('Audit_AI_Actions', 'Begrunnelse', 'Column'),
                ]
            }, {'x': 0, 'y': 0, 'z': 1, 'width': 1570, 'height': 800, 'tabOrder': 1}, 'Audit trail – data source not configured')

    (pages_dir / 'pages.json').write_text(json.dumps({
        '$schema': 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json',
        'pageOrder': page_order,
        'activePageName': page_order[0],
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def enhance_workbooks():
    for workbook_path in [DATA_DIR / 'Rapport Enhet Bo og Miljø.xlsx', DATA_DIR / 'Rapport Enhet Skole.xlsx']:
        wb = load_workbook(workbook_path)
        matrix = wb['KPI Matrix']
        if matrix.max_row > 1:
            matrix.conditional_formatting.add(
                f'D2:D{matrix.max_row}',
                DataBarRule(start_type='num', start_value=0, end_type='max', color='FF95A5A6', showValue=True),
            )
            matrix.conditional_formatting.add(
                f'E2:E{matrix.max_row}',
                IconSetRule(icon_style='3TrafficLights1', type='formula', values=['=Parameters!$B$3', '=Parameters!$B$2'], showValue=True, percent=False, reverse=True),
            )
        matrix.freeze_panes = 'A2'
        for col in matrix.columns:
            letter = get_column_letter(col[0].column)
            max_length = max((len(str(cell.value)) for cell in col if cell.value is not None), default=8)
            matrix.column_dimensions[letter].width = min(max(max_length + 2, 12), 38)
        data_ws = wb['Data']
        data_ws.auto_filter.ref = data_ws.dimensions
        for col in data_ws.columns:
            letter = get_column_letter(col[0].column)
            max_length = max((len(str(cell.value)) for cell in list(col)[:80] if cell.value is not None), default=8)
            data_ws.column_dimensions[letter].width = min(max(max_length + 2, 12), 34)
        if 'Parameters' not in wb.sheetnames:
            params = wb.create_sheet('Parameters')
            params.append(['Parameter', 'Value', 'Description'])
            params.append(['High variance threshold', 0.02, 'Red status above 2% adverse variance'])
            params.append(['Observation threshold', 0.00, 'Amber status for adverse variance between 0% and 2%'])
            params.append(['Forecast persistence', 0.50, 'Share of positive YTD variance carried into the forecast'])
            for cell in params[1]:
                cell.font = Font(bold=True, color='FF1B365D')
                cell.fill = PatternFill('solid', fgColor='FFD9EAF7')
            params['B2'].number_format = '0.0%'
            params['B3'].number_format = '0.0%'
            params['B4'].number_format = '0%'
            params.column_dimensions['A'].width = 30
            params.column_dimensions['B'].width = 14
            params.column_dimensions['C'].width = 66
        wb.save(workbook_path)


def main():
    build_bo_miljo_workbook(DATA_DIR / 'Rapport Enhet Bo og Miljø.xlsx')
    build_skole_workbook(DATA_DIR / 'Rapport Enhet Skole.xlsx')
    enhance_workbooks()

    write_pbip(POWERBI_DIR, 'Bo og Miljø enhet project', 'Bo og Miljø enhet project.Report', 'Bo og Miljø enhet project.SemanticModel')
    write_pbip(POWERBI_DIR, 'Skole enhet project', 'Skole enhet project.Report', 'Skole enhet project.SemanticModel')

    # Ensure project folders retain current names with spaces for the actual Power BI files
    # The pbip serialization is written in the project folders above.


if __name__ == '__main__':
    main()
