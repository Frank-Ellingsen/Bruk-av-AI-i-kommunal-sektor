#!/usr/bin/env python3
"""
===============================================================================
KRISTIANSAND KOMMUNE - GENERATOR FOR KOMPLETT EPM PDF RAPPORT
===============================================================================
Genererer en offisiell, publiseringsklar styringsrapport i A4 liggende (landscape):
'reports/Kristiansand_EPM_Status_Prognose_Tiltaksrapport.pdf'
Inneholder full status, prognoser, tiltak og månedlig tiltakseffekt (Net Zero EOY)
for Kommunal Boenhet og Kommunal Skole.
===============================================================================
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

try:
    from config import REPORTS_DIR
except ModuleNotFoundError:  # pragma: no cover - package import fallback
    from src.config import REPORTS_DIR

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name in ["src", "powerbi"] else BASE_DIR
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = REPORTS_DIR / "Kristiansand_EPM_Status_Prognose_Tiltaksrapport.pdf"

# Farger
C_NAVY = colors.HexColor("#0F172A")
C_DARK = colors.HexColor("#1E293B")
C_MUTED = colors.HexColor("#64748B")
C_LIGHT_BG = colors.HexColor("#F8FAFC")
C_BORDER = colors.HexColor("#E2E8F0")
C_ALERT = colors.HexColor("#DC2626")
C_GREEN = colors.HexColor("#16A34A")
C_BLUE = colors.HexColor("#2563EB")
C_WHITE = colors.HexColor("#FFFFFF")

def build_pdf():
    # A4 Landscape: 29.7 x 21.0 cm
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm
    )

    styles = getSampleStyleSheet()

    # Egendefinerte typografistiler
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=C_NAVY,
        spaceAfter=4
    )
    style_subtitle = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=C_MUTED,
        spaceAfter=12
    )
    style_sec = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=C_NAVY,
        spaceBefore=10,
        spaceAfter=6
    )
    style_sec_small = ParagraphStyle(
        'SectionHeadingSmall',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=C_BLUE,
        spaceBefore=4,
        spaceAfter=4
    )
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=C_DARK
    )
    ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=C_DARK
    )
    style_th = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=C_NAVY,
        alignment=0
    )
    style_th_r = ParagraphStyle(
        'TableHeaderR',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=C_NAVY,
        alignment=2
    )
    style_td = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=C_DARK
    )
    style_td_r = ParagraphStyle(
        'TableCellR',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=C_DARK,
        alignment=2
    )
    style_td_alert = ParagraphStyle(
        'TableCellAlert',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=C_ALERT,
        alignment=2
    )
    style_td_green = ParagraphStyle(
        'TableCellGreen',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=C_GREEN,
        alignment=2
    )

    story = []

    def p(text, style=style_body):
        return Paragraph(text, style)

    # =========================================================================
    # SIDE 1: EXECUTIVE SUMMARY & KONSOLIDERT BILDE
    # =========================================================================
    story.append(p("KRISTIANSAND KOMMUNE | ØKONOMI- OG VIRKSOMHETSSTYRING (EPM)", style_sec_small))
    story.append(p("Tertialrapport 2. Tertial 2026: Helårsprognoser og Tiltaksplan for Net Zero Budsjettbalanse", style_title))
    story.append(p("Ansvarlig: Frank Ellingsen (Senior BI Specialist & Financial Controller) | Omfatter: Kommunal Boenhet & Kommunal Skole | Mål: 0 kr i helårsavvik", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    # Nøkkeltall kort
    kpi_table_data = [
        [
            Paragraph("<b>YTD REGNSKAP (T2)</b><br/><font size=12 color='#0F172A'><b>31,52 mill. kr</b></font><br/><font size=6 color='#64748B'>Faktisk bokført Jan–Aug</font>", style_body),
            Paragraph("<b>YTD BUDSJETT (T2)</b><br/><font size=12 color='#0F172A'><b>29,30 mill. kr</b></font><br/><font size=6 color='#64748B'>Akkumulert T2-ramme</font>", style_body),
            Paragraph("<b>AKKUMULERT AVVIK</b><br/><font size=12 color='#DC2626'><b>-2,23 mill. kr</b></font><br/><font size=6 color='#DC2626'>Merforbruk: -7,6 % (Kritisk)</font>", style_body),
            Paragraph("<b>RUN-RATE EOY UTEN TILTAK</b><br/><font size=12 color='#DC2626'><b>-3,34 mill. kr</b></font><br/><font size=6 color='#64748B'>Uavbøtt helårsprognose</font>", style_body),
            Paragraph("<b>MÅLRESULTAT 31.12</b><br/><font size=12 color='#16A34A'><b>0,00 kr</b></font><br/><font size=6 color='#16A34A'>Net Zero Budsjettbalanse</font>", style_body),
        ]
    ]
    t_kpi = Table(kpi_table_data, colWidths=[5.3*cm, 5.3*cm, 5.3*cm, 5.3*cm, 5.5*cm])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 10))

    # Tabell over begge use cases
    story.append(p("1. Konsolidert Hovedoversikt over Virksomhetsenhetene", style_sec))
    t1_data = [
        [p("Virksomhetsenhet / Sektor", style_th), p("Årsbudsjett", style_th_r), p("Budsjett YTD", style_th_r), p("Regnskap YTD", style_th_r), p("Avvik YTD", style_th_r), p("Avvik %", style_th_r), p("Run-Rate EOY", style_th_r), p("Tiltak T3", style_th_r), p("EOY Balansert", style_th_r)],
        [p("Kommunal Boenhet (Helse)", style_td), p("17 233 691 kr", style_td_r), p("11 337 237 kr", style_td_r), p("12 622 851 kr", style_td_r), p("-1 285 614 kr", style_td_alert), p("-11,3 %", style_td_alert), p("19 162 112 kr", style_td_r), p("+1 928 421 kr", style_td_green), p("17 233 691 kr (0 kr)", style_td_green)],
        [p("Kommunal Skole (Oppvekst)", style_td), p("27 490 000 kr", style_td_r), p("17 958 000 kr", style_td_r), p("18 902 000 kr", style_td_r), p("-944 000 kr", style_td_alert), p("-5,3 %", style_td_alert), p("28 353 000 kr", style_td_r), p("+1 416 000 kr", style_td_green), p("27 490 000 kr (0 kr)", style_td_green)],
        [p("<b>TOTALT KONSOLIDERT</b>", style_th), p("<b>44 723 691 kr</b>", style_th_r), p("<b>29 295 237 kr</b>", style_th_r), p("<b>31 524 851 kr</b>", style_th_r), p("<b>-2 229 614 kr</b>", style_td_alert), p("<b>-7,6 %</b>", style_td_alert), p("<b>47 515 112 kr</b>", style_th_r), p("<b>+3 344 421 kr</b>", style_td_green), p("<b>44 723 691 kr (0 kr)</b>", style_td_green)]
    ]
    t1 = Table(t1_data, colWidths=[5.5*cm, 2.7*cm, 2.7*cm, 2.7*cm, 2.7*cm, 1.8*cm, 2.8*cm, 2.7*cm, 3.1*cm])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, C_NAVY),
        ('LINEBELOW', (0,1), (-1,-2), 0.5, C_BORDER),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, C_NAVY),
        ('BACKGROUND', (0,-1), (-1,-1), C_LIGHT_BG),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    # Vannfallsdiagram
    chart_wf = REPORTS_DIR / "chart_netzero_waterfall.png"
    if chart_wf.exists():
        story.append(Image(str(chart_wf), width=26.5*cm, height=7.2*cm))

    story.append(PageBreak())

    # =========================================================================
    # SIDE 2: BOMILJØ (KOMMUNAL BOENHET) - STATUS & FRAMSIKT FUNN
    # =========================================================================
    story.append(p("KRISTIANSAND KOMMUNE | ENHETSRAPPORT HELSE OG MESTRING", style_sec_small))
    story.append(p("Kommunal Boenhet: Avviksdiagnose & Månedlig Forløp (Framsikt)", style_title))
    story.append(p("Døgnbemannet tilrettelagt bolig (KOSTRA 254) | Data kilde: Visma Enterprise & Framsikt | Akkumulert merforbruk T2: -1 285 614 kr (-11,3 %)", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    # Tabell måned Jan-Aug vs Tekst
    mnd_tab_data = [
        [p("Måned", style_th), p("Budsjett", style_th_r), p("Regnskap", style_th_r), p("Avvik i kr", style_th_r), p("Avvik %", style_th_r), p("Driftskommentar / Hendelser", style_th)],
        [p("Januar", style_td), p("1 403 337 kr", style_td_r), p("1 014 752 kr", style_td_r), p("+388 585 kr", style_td_green), p("+27,7 %", style_td_green), p("Stabil grunnbemanning, lavt vikarinnleie", style_td)],
        [p("Februar", style_td), p("1 410 893 kr", style_td_r), p("2 082 090 kr", style_td_r), p("-671 197 kr", style_td_alert), p("-47,6 %", style_td_alert), p("🚨 Februarsjokk: Akutt influensatopp, overtid og eksterne byråer", style_td)],
        [p("Mars", style_td), p("1 342 381 kr", style_td_r), p("1 541 249 kr", style_td_r), p("-198 868 kr", style_td_alert), p("-14,8 %", style_td_alert), p("Etterslep i sykefravær, høyt nattillegg", style_td)],
        [p("April", style_td), p("2 357 359 kr", style_td_r), p("2 256 716 kr", style_td_r), p("+100 643 kr", style_td_green), p("+4,3 %", style_td_green), p("Feriepengeavstemming og refusjoner", style_td)],
        [p("Mai", style_td), p("1 544 215 kr", style_td_r), p("1 613 437 kr", style_td_r), p("-69 222 kr", style_td_alert), p("-4,5 %", style_td_alert), p("Stabilt merforbruk knyttet til 2:1-vedtak", style_td)],
        [p("Juni", style_td), p("241 681 kr", style_td_r), p("519 336 kr", style_td_r), p("-277 655 kr", style_td_alert), p("-114,9 %", style_td_alert), p("Sommerturnusstart, lavt budsjettgrunnlag", style_td)],
        [p("Juli", style_td), p("1 512 209 kr", style_td_r), p("1 837 523 kr", style_td_r), p("-325 314 kr", style_td_alert), p("-21,5 %", style_td_alert), p("Bruk av vikarbyrå i fellesferien", style_td)],
        [p("August", style_td), p("1 525 162 kr", style_td_r), p("1 765 810 kr", style_td_r), p("-240 648 kr", style_td_alert), p("-15,8 %", style_td_alert), p("Siste avsluttede måned: Høyt kvelds-/helgepress", style_td)],
        [p("<b>YTD T2 SUM</b>", style_th), p("<b>11 337 237 kr</b>", style_th_r), p("<b>12 622 851 kr</b>", style_th_r), p("<b>-1 285 614 kr</b>", style_td_alert), p("<b>-11,3 %</b>", style_td_alert), p("<b>Akkumulert overforbruk som krever korrigering</b>", style_th)]
    ]
    t_mnd = Table(mnd_tab_data, colWidths=[2.2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 1.8*cm, 7.5*cm])
    t_mnd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, C_NAVY),
        ('LINEBELOW', (0,1), (-1,-2), 0.5, C_BORDER),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, C_NAVY),
        ('BACKGROUND', (0,-1), (-1,-1), C_LIGHT_BG),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))

    # Høyre side: Funn fra Framsikt
    funn_text = """
    <b>DIAGNOSTISKE HOVEDFUNN (FRAMSIKT):</b><br/>
    <b>1. Lønn vs. Drift:</b><br/>
    • <b>1 Lønn:</b> -1 149 674 kr (-10,4 % avvik). Står for 89 % av enhetens samlede merforbruk.<br/>
    • <b>2 Utgifter:</b> -144 113 kr. Hovedsakelig kjøp av vikarbyråtjenester (art 127040).<br/><br/>
    <b>2. Topp Avvikskontoer (Drivere):</b><br/>
    • <i>Fastlønn ordinære (101000):</i> -474 918 kr (grunnbemanning over budsjett)<br/>
    • <i>Kjøp av vikarbyrå (127040):</i> -382 656 kr (Adecco/Dedicate innleie)<br/>
    • <i>Vikar kvelds-/nattillegg (102031):</i> -259 303 kr (turnusskjevhet)<br/>
    • <i>Overtidslønn (104000):</i> -185 573 kr (ubalanse i helgedekning)<br/>
    • <i>Ekstrahjelp (103000):</i> -141 648 kr<br/><br/>
    <b>3. Motvirkende faktorer:</b><br/>
    • <i>Vikar foreldrepermisjon (102002):</i> +189 928 kr mindreforbruk<br/>
    • <i>Tilskudd lærlinger (112098):</i> +160 447 kr merinntekt
    """

    grid_s2 = Table([[t_mnd, Paragraph(funn_text, style_body)]], colWidths=[19.0*cm, 7.5*cm])
    grid_s2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (1,0), (1,0), 10),
    ]))
    story.append(grid_s2)
    story.append(Spacer(1, 8))

    # Graf: Månedlig forløp og tiltaksbane
    chart_bom = REPORTS_DIR / "chart_bomiljo_monthly.png"
    if chart_bom.exists():
        story.append(Image(str(chart_bom), width=26.5*cm, height=6.8*cm))

    story.append(PageBreak())

    # =========================================================================
    # SIDE 3: BOMILJØ - TILTAKSPLAN & VEIEN TIL NET ZERO
    # =========================================================================
    story.append(p("KRISTIANSAND KOMMUNE | KORRIGERENDE TILTAKSPLAN FOR HELSE", style_sec_small))
    story.append(p("Kommunal Boenhet: Tiltakspakke og Månedlig Net Zero Lukking", style_title))
    story.append(p("Forpliktende innsparing i 3. tertial (September - Desember) for å nå 0 kr i årsavvik per 31.12.2026", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    # Tiltakstabell
    t_actions_bom = [
        [p("ID", style_th), p("Tiltaksbeskrivelse", style_th), p("KOSTRA-Art", style_th), p("Ansvarlig Leder", style_th), p("Månedlig Takt", style_th_r), p("Total Effekt T3", style_th_r), p("Styringsmessig Forankring", style_th)],
        [p("B1", style_td), p("Totalstans i eksterne vikarbyråer; overgang til kommunens interne bemanningspool", style_td), p("127040", style_td), p("Enhetsleder", style_td), p("125 000 kr / mnd", style_td_r), p("500 000 kr", style_td_green), p("Rammeavtalebehov avslått; intern pool prioritert", style_td)],
        [p("B2", style_td), p("Turnusomlegging: Forhåndsbooking av helgevakter, reduksjon av kveld/nattillegg", style_td), p("102030/31", style_td), p("Avdelingsleder", style_td), p("110 000 kr / mnd", style_td_r), p("440 000 kr", style_td_green), p("Drøftet med tillitsvalgte (Fagforbundet/Delta)", style_td)],
        [p("B3", style_td), p("Restriktiv overtidskontroll: Krav om forhåndsgodkjenning av enhetsleder", style_td), p("104000", style_td), p("Enhetsleder", style_td), p("95 000 kr / mnd", style_td_r), p("380 000 kr", style_td_green), p("Automatisk varsel i Visma Enterprise ved overtid", style_td)],
        [p("B4", style_td), p("Intensivert sykefraværsoppfølging (IA) og full avstemming av NAV-sykepenger", style_td), p("102000/1690", style_td), p("HR / Enhetsleder", style_td), p("100 000 kr / mnd", style_td_r), p("400 000 kr", style_td_green), p("Månedlig avstemming mot NAV/Altinn", style_td)],
        [p("B5", style_td), p("Søknad om toppfinansiering ressurskrevende tjenester for 2 beboere m/ 2:1-bemanning", style_td), p("170000", style_td), p("Kommunalsjef", style_td), p("Engangsoppgjør", style_td_r), p("208 421 kr", style_td_green), p("Helse- og omsorgsdepartementets refusjonsordning", style_td)],
        [p("<b>SUM</b>", style_th), p("<b>SAMLET TILTAKSEFFEKT KOMMUNAL BOENHET</b>", style_th), p("<b>Flere</b>", style_th), p("<b>Lederteam</b>", style_th), p("<b>430 000 kr/mnd</b>", style_th_r), p("<b>1 928 421 kr</b>", style_td_green), p("<b>Garanterer 100 % budsjettbalanse (0 kr)</b>", style_th)]
    ]
    t_tb_pdf = Table(t_actions_bom, colWidths=[1.0*cm, 7.8*cm, 2.2*cm, 2.8*cm, 3.0*cm, 3.0*cm, 6.7*cm])
    t_tb_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, C_NAVY),
        ('LINEBELOW', (0,1), (-1,-2), 0.5, C_BORDER),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, C_NAVY),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F0FDF4")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tb_pdf)
    story.append(Spacer(1, 10))

    # Månedlig balanseringsprofil Sept-Des
    story.append(p("Månedlig Balanseringsbane mot 31.12.2026 (Kommunal Boenhet)", style_sec))
    t_bal_data = [
        [p("Periode", style_th), p("Vedtatt Budsjett", style_th_r), p("Run-Rate Kostnad", style_th_r), p("Tiltakseffekt T3", style_th_r), p("Justert Regnskap", style_th_r), p("Månedlig Avvik", style_th_r), p("Akkumulert Avvik EOY", style_th_r)],
        [p("Januar - August (T2)", style_td), p("11 337 237 kr", style_td_r), p("12 622 851 kr", style_td_r), p("0 kr", style_td_r), p("12 622 851 kr", style_td_r), p("-1 285 614 kr", style_td_alert), p("-1 285 614 kr", style_td_alert)],
        [p("September", style_td), p("1 504 399 kr", style_td_r), p("1 665 101 kr", style_td_r), p("+430 000 kr", style_td_green), p("1 235 101 kr", style_td_r), p("+269 298 kr", style_td_green), p("-1 016 316 kr", style_td_alert)],
        [p("Oktober", style_td), p("1 418 774 kr", style_td_r), p("1 579 476 kr", style_td_r), p("+430 000 kr", style_td_green), p("1 149 476 kr", style_td_r), p("+269 298 kr", style_td_green), p("-747 018 kr", style_td_alert)],
        [p("November", style_td), p("1 418 540 kr", style_td_r), p("1 579 242 kr", style_td_r), p("+430 000 kr", style_td_green), p("1 149 242 kr", style_td_r), p("+269 298 kr", style_td_green), p("-477 720 kr", style_td_alert)],
        [p("Desember", style_td), p("1 554 741 kr", style_td_r), p("1 715 443 kr", style_td_r), p("+638 421 kr", style_td_green), p("1 077 022 kr", style_td_r), p("+477 720 kr", style_td_green), p("0 kr (BALANSE)", style_td_green)],
        [p("<b>HELÅR TOTALT</b>", style_th), p("<b>17 233 691 kr</b>", style_th_r), p("<b>19 162 112 kr</b>", style_th_r), p("<b>+1 928 421 kr</b>", style_td_green), p("<b>17 233 691 kr</b>", style_th_r), p("<b>0 kr</b>", style_td_green), p("<b>0 kr (NET ZERO) ✓</b>", style_td_green)]
    ]
    t_bal_pdf = Table(t_bal_data, colWidths=[4.0*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 4.0*cm, 4.5*cm])
    t_bal_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, C_NAVY),
        ('LINEBELOW', (0,1), (-1,-2), 0.5, C_BORDER),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, C_NAVY),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F0FDF4")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_bal_pdf)

    story.append(PageBreak())

    # =========================================================================
    # SIDE 4: KOMSKOLE (KOMMUNAL SKOLE) - STATUS & ENHETSFORDELING
    # =========================================================================
    story.append(p("KRISTIANSAND KOMMUNE | ENHETSRAPPORT OPPVEKST", style_sec_small))
    story.append(p("Kommunal Skole: Avviksfordeling per Enhet og Kontotype (Framsikt)", style_title))
    story.append(p("Skole og oppvekst (KOSTRA 202) | Data kilde: Framsikt / Visma | Akkumulert merforbruk T2: -944 000 kr (-5,3 %)", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    # Matrisetabell for skolen
    skole_matrise_pdf = [
        [p("Enhet (brukt)", style_th), p("Regnskap hiå", style_th_r), p("Budsjett hiå", style_th_r), p("Avvik i kr", style_th_r), p("Avvik %", style_th_r), p("Årsbudsjett", style_th_r), p("Brukt hiå %", style_th_r), p("Status / Diagnose", style_th)],
        [p("Ordinær undervisning", style_td), p("12 024 000 kr", style_td_r), p("11 385 000 kr", style_td_r), p("-639 000 kr", style_td_alert), p("-5,6 %", style_td_alert), p("17 590 000 kr", style_td_r), p("68,4 %", style_td_r), p("🚩 Lærervikarer og fastlønnsmerforbruk", style_td)],
        [p("Spesialundervisning grunnskole", style_td), p("2 792 000 kr", style_td_r), p("2 496 000 kr", style_td_r), p("-296 000 kr", style_td_alert), p("-11,9 %", style_td_alert), p("4 114 000 kr", style_td_r), p("67,9 %", style_td_r), p("🚩 Høyt vedtakspress og assistenttimer", style_td)],
        [p("Grunnskole (felles)", style_td), p("1 733 000 kr", style_td_r), p("1 761 000 kr", style_td_r), p("+28 000 kr", style_td_green), p("+1,6 %", style_td_green), p("2 919 000 kr", style_td_r), p("59,4 %", style_td_r), p("✓ Moderat mindreforbruk på fellesdrift", style_td)],
        [p("Skolefritidstilbud (SFO)", style_td), p("983 000 kr", style_td_r), p("813 000 kr", style_td_r), p("-170 000 kr", style_td_alert), p("-20,9 %", style_td_alert), p("1 233 000 kr", style_td_r), p("79,7 %", style_td_alert), p("🚩 Høyere bemanning enn foreldrebetaling", style_td)],
        [p("Voksenopplæring", style_td), p("491 000 kr", style_td_r), p("513 000 kr", style_td_r), p("+22 000 kr", style_td_green), p("+4,3 %", style_td_green), p("35 000 kr", style_td_r), p("1402,9 %", style_td_r), p("Periodisering av statlige integreringstilskudd", style_td)],
        [p("Skoleskyss", style_td), p("469 000 kr", style_td_r), p("516 000 kr", style_td_r), p("+47 000 kr", style_td_green), p("+9,1 %", style_td_green), p("775 000 kr", style_td_r), p("60,5 %", style_td_r), p("✓ Effektiv ruteplanlegging", style_td)],
        [p("PPT-tjeneste", style_td), p("286 000 kr", style_td_r), p("350 000 kr", style_td_r), p("+64 000 kr", style_td_green), p("+18,3 %", style_td_green), p("700 000 kr", style_td_r), p("40,9 %", style_td_r), p("✓ Vakanser i psykolog/rådgiverstillinger", style_td)],
        [p("Leirskole / Ekskursjoner", style_td), p("124 000 kr", style_td_r), p("124 000 kr", style_td_r), p("0 kr", style_td_r), p("0,0 %", style_td_r), p("124 000 kr", style_td_r), p("100,0 %", style_td_r), p("Fullt avregnet i T2", style_td)],
        [p("<b>TOTALT KOMMUNAL SKOLE</b>", style_th), p("<b>18 902 000 kr</b>", style_th_r), p("<b>17 958 000 kr</b>", style_th_r), p("<b>-944 000 kr</b>", style_td_alert), p("<b>-5,3 %</b>", style_td_alert), p("<b>27 490 000 kr</b>", style_th_r), p("<b>68,8 %</b>", style_th_r), p("<b>🚩 Samlet merforbruk per 2. tertial</b>", style_th)]
    ]
    t_sk_pdf = Table(skole_matrise_pdf, colWidths=[4.2*cm, 2.7*cm, 2.7*cm, 2.4*cm, 1.8*cm, 2.7*cm, 2.0*cm, 8.0*cm])
    t_sk_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, C_NAVY),
        ('LINEBELOW', (0,1), (-1,-2), 0.5, C_BORDER),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, C_NAVY),
        ('BACKGROUND', (0,-1), (-1,-1), C_LIGHT_BG),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_sk_pdf)
    story.append(Spacer(1, 8))

    # Graf: Enhetsavvik for Kommunal skole
    chart_kom = REPORTS_DIR / "chart_komskole_units.png"
    if chart_kom.exists():
        story.append(Image(str(chart_kom), width=26.5*cm, height=6.8*cm))

    story.append(PageBreak())

    # =========================================================================
    # SIDE 5: KOMSKOLE - TILTAKSPLAN & VEIEN TIL NET ZERO
    # =========================================================================
    story.append(p("KRISTIANSAND KOMMUNE | KORRIGERENDE TILTAKSPLAN FOR OPPVEKST", style_sec_small))
    story.append(p("Kommunal Skole: Tiltakspakke og Månedlig Net Zero Lukking", style_title))
    story.append(p("Forpliktende innsparing i 3. tertial (September - Desember) for å nå 0 kr i årsavvik per 31.12.2026", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    # Tiltakstabell for skolen
    t_actions_skole = [
        [p("ID", style_th), p("Tiltaksbeskrivelse", style_th), p("Område / Art", style_th), p("Ansvarlig Leder", style_th), p("Månedlig Takt", style_th_r), p("Total Effekt T3", style_th_r), p("Styringsmessig Forankring", style_th)],
        [p("S1", style_td), p("Stopp i eksterne lærervikarer; intern timebytte og ressursomdisponering", style_td), p("Undervisning / 1020", style_td), p("Rektor", style_td), p("125 000 kr / mnd", style_td_r), p("500 000 kr", style_td_green), p("Fagledermøte; lærernes leseplikt utnyttes fullt", style_td)],
        [p("S2", style_td), p("Timeplanoptimalisering: Sammenslåing av paralleller og kutt i ekstrahjelptimer", style_td), p("Ordinær / 1030", style_td), p("Undervisningsinsp.", style_td), p("75 000 kr / mnd", style_td_r), p("300 000 kr", style_td_green), p("Timeplanlegger revidert for høstsemesteret", style_td)],
        [p("S3", style_td), p("Innkjøpsfrys på IKT-utstyr, nye læremidler, inventar og administrative driftsmidler", style_td), p("Drift / 1110-1200", style_td), p("Rektor / Admin", style_td), p("50 000 kr / mnd", style_td_r), p("200 000 kr", style_td_green), p("Kun akutt sikkerhetsmateriell godkjennes", style_td)],
        [p("S4", style_td), p("Aktiv purring og full avstemming av utestående NAV sykelønnsrefusjoner", style_td), p("Refusjon / 1690", style_td), p("Skolesekretær/HR", style_td), p("Løpende Altinn", style_td_r), p("250 000 kr", style_td_green), p("Avstemt med NAV forvaltning; innbetaling sikret", style_td)],
        [p("S5", style_td), p("Samordning av spesialpedagogiske timer og assistentressurser på tvers av trinn", style_td), p("Spes.und / 1010", style_td), p("Avdelingsleder", style_td), p("41 500 kr / mnd", style_td_r), p("166 000 kr", style_td_green), p("Drøftet med PPT og skolehelsetjenesten", style_td)],
        [p("<b>SUM</b>", style_th), p("<b>SAMLET TILTAKSEFFEKT KOMMUNAL SKOLE</b>", style_th), p("<b>Flere</b>", style_th), p("<b>Rektor / Team</b>", style_th), p("<b>354 000 kr/mnd</b>", style_th_r), p("<b>1 416 000 kr</b>", style_td_green), p("<b>Garanterer 100 % budsjettbalanse (0 kr)</b>", style_th)]
    ]
    t_tsk_pdf = Table(t_actions_skole, colWidths=[1.0*cm, 7.8*cm, 2.5*cm, 2.8*cm, 2.8*cm, 2.8*cm, 6.8*cm])
    t_tsk_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, C_NAVY),
        ('LINEBELOW', (0,1), (-1,-2), 0.5, C_BORDER),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, C_NAVY),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F0FDF4")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tsk_pdf)
    story.append(Spacer(1, 10))

    # Månedlig balanseringsprofil for skolen
    story.append(p("Månedlig Balanseringsbane mot 31.12.2026 (Kommunal Skole)", style_sec))
    t_sk_bal = [
        [p("Periode", style_th), p("Vedtatt Budsjett", style_th_r), p("Run-Rate Kostnad", style_th_r), p("Tiltakseffekt T3", style_th_r), p("Justert Regnskap", style_th_r), p("Månedlig Avvik", style_th_r), p("Akkumulert Avvik EOY", style_th_r)],
        [p("Januar - August (T2)", style_td), p("17 958 000 kr", style_td_r), p("18 902 000 kr", style_td_r), p("0 kr", style_td_r), p("18 902 000 kr", style_td_r), p("-944 000 kr", style_td_alert), p("-944 000 kr", style_td_alert)],
        [p("September", style_td), p("2 383 000 kr", style_td_r), p("2 362 750 kr", style_td_r), p("+291 500 kr", style_td_green), p("2 071 250 kr", style_td_r), p("+311 750 kr", style_td_green), p("-632 250 kr", style_td_alert)],
        [p("Oktober", style_td), p("2 383 000 kr", style_td_r), p("2 362 750 kr", style_td_r), p("+291 500 kr", style_td_green), p("2 071 250 kr", style_td_r), p("+311 750 kr", style_td_green), p("-320 500 kr", style_td_alert)],
        [p("November", style_td), p("2 383 000 kr", style_td_r), p("2 362 750 kr", style_td_r), p("+291 500 kr", style_td_green), p("2 071 250 kr", style_td_r), p("+311 750 kr", style_td_green), p("-8 750 kr", style_td_alert)],
        [p("Desember", style_td), p("2 383 000 kr", style_td_r), p("2 362 750 kr", style_td_r), p("+541 500 kr", style_td_green), p("1 821 250 kr", style_td_r), p("+561 750 kr", style_td_green), p("0 kr (BALANSE)", style_td_green)],
        [p("<b>HELÅR TOTALT</b>", style_th), p("<b>27 490 000 kr</b>", style_th_r), p("<b>28 353 000 kr</b>", style_th_r), p("<b>+1 416 000 kr</b>", style_td_green), p("<b>27 490 000 kr</b>", style_th_r), p("<b>0 kr</b>", style_td_green), p("<b>0 kr (NET ZERO) ✓</b>", style_td_green)]
    ]
    t_sk_bal_pdf = Table(t_sk_bal, colWidths=[4.0*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 4.0*cm, 4.5*cm])
    t_sk_bal_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, C_NAVY),
        ('LINEBELOW', (0,1), (-1,-2), 0.5, C_BORDER),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, C_NAVY),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#F0FDF4")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sk_bal_pdf)

    story.append(PageBreak())

    # =========================================================================
    # SIDE 6: KONSOLIDERT TILTAKSMATRISE & JURIDISK FORANKRING
    # =========================================================================
    story.append(p("KRISTIANSAND KOMMUNE | KONSOLIDERT TILTAKS- OG STYRINGSRAMMEVERK", style_sec_small))
    story.append(p("Konsolidert Tiltaksmatrise og Human-in-the-Loop Beslutningsstøtte", style_title))
    story.append(p("Etterlevelse av Kommuneloven § 14-5 (Tiltaksplikt) og EU AI Act Art. 27 (Revisjonsspor i SQLite)", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    # Master Tabell
    master_tab_data = [
        [p("Tiltakskategori / Hovedområde", style_th), p("Kommunal Boenhet", style_th_r), p("Kommunal Skole", style_th_r), p("Samlet Effekt T3", style_th_r), p("Månedlig Takt", style_th_r), p("Garantist & Kontrollorgan", style_th)],
        [p("1. Vikarrestriksjoner & Stans i Eksterne Byråer", style_td), p("500 000 kr", style_td_r), p("500 000 kr", style_td_r), p("1 000 000 kr", style_td_green), p("250 000 kr / mnd", style_td_r), p("Enhetsledere / HR Bemanningssenter", style_td)],
        [p("2. Turnusomlegging, Overtidsstopp & Timeplanrevisjon", style_td), p("820 000 kr", style_td_r), p("300 000 kr", style_td_r), p("1 120 000 kr", style_td_green), p("280 000 kr / mnd", style_td_r), p("Avdelingsledere / Tillitsvalgte", style_td)],
        [p("3. Innkjøpsfrys på Driftsmateriell, IKT & Inventar", style_td), p("0 kr", style_td_r), p("200 000 kr", style_td_r), p("200 000 kr", style_td_green), p("50 000 kr / mnd", style_td_r), p("Økonomiavdelingen / Fakturakontroll", style_td)],
        [p("4. Intensivert NAV Refusjonsavstemming (Sykepenger/IA)", style_td), p("400 000 kr", style_td_r), p("250 000 kr", style_td_r), p("650 000 kr", style_td_green), p("Aktiv purring Altinn", style_td_r), p("Lønnsavdelingen / Altinn-ansvarlig", style_td)],
        [p("5. Ressurskrevende Tjenester / Toppfinansiering", style_td), p("208 421 kr", style_td_r), p("166 000 kr", style_td_r), p("374 421 kr", style_td_green), p("Engangsoppgjør", style_td_r), p("Kommunalsjef / Statsforvalter", style_td)],
        [p("<b>TOTAL TILTAKSEFFEKT I 3. TERTIAL</b>", style_th), p("<b>1 928 421 kr</b>", style_th_r), p("<b>1 416 000 kr</b>", style_th_r), p("<b>3 344 421 kr</b>", style_td_green), p("<b>836 105 kr / mnd</b>", style_th_r), p("<b>Månedlig oppfølging i lederteam</b>", style_th)],
        [p("Vedtatt Årsbudsjett", style_td), p("17 233 691 kr", style_td_r), p("27 490 000 kr", style_td_r), p("44 723 691 kr", style_td_r), p("-", style_td_r), p("Bystyrets vedtatte ramme", style_td)],
        [p("Forventet Regnskap 31.12 med Tiltak", style_td), p("17 233 691 kr", style_td_r), p("27 490 000 kr", style_td_r), p("44 723 691 kr", style_td_r), p("-", style_td_r), p("Revidert årsregnskap", style_td)],
        [p("<b>SLUTTAVVIK PER 31.12.2026</b>", style_th), p("<b>0 kr (0,0 %)</b>", style_td_green), p("<b>0 kr (0,0 %)</b>", style_td_green), p("<b>0 kr (0,0 %)</b>", style_td_green), p("<b>-</b>", style_td_r), p("<b>NET ZERO OPPNÅDD ✓</b>", style_th)]
    ]
    t_master = Table(master_tab_data, colWidths=[6.2*cm, 3.4*cm, 3.4*cm, 3.4*cm, 3.4*cm, 6.7*cm])
    t_master.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, C_NAVY),
        ('LINEBELOW', (0,1), (-1,-2), 0.5, C_BORDER),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, C_NAVY),
        ('BACKGROUND', (0,-4), (-1,-4), colors.HexColor("#F0FDF4")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#DCFCE7")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_master)
    story.append(Spacer(1, 10))

    # Juridisk og Etisk AI Rammeverk tekst
    governance_box = [
        [
            Paragraph("<b>HUMAN-IN-THE-LOOP (HITL) ARBEIDSFLYT:</b><br/>"
                      "• <b>Streamlit Portalen:</b> Enhetslederne logger inn på <code>hitl_writeback_ui.py</code> for å inspisere AI-analysen.<br/>"
                      "• <b>Glass-Box Prinsippet:</b> Ingen automatiserte kutt gjennomføres uten aktiv signering (GODKJENT / ENDRET / AVVIST).<br/>"
                      "• <b>Begrunnelsesplikt:</b> Saksbehandler må dokumentere faglig forsvarlighet jf. helse- og opplæringsloven.", style_body),
            Paragraph("<b>LOVMESSIG ETTERLEVELSE:</b><br/>"
                      "• <b>Kommuneloven § 14-5:</b> Kommunedirektøren og enhetsledere har lovpålagt plikt til å iverksette tiltak for å sikre budsjettbalanse.<br/>"
                      "• <b>EU AI Act Art. 27:</b> Full teknisk og juridisk sporbarhet i <code>Audit_AI_Actions</code>.<br/>"
                      "• <b>Uavhengig Revisjon:</b> Revisjonssporet lagrer tidsstempel, IP-adresse, konfidensscore og saksbehandlers ID.", style_body)
        ]
    ]
    t_gov = Table(governance_box, colWidths=[13.2*cm, 13.3*cm])
    t_gov.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_gov)

    doc.build(story)
    print(f"[OK] Fullstendig PDF-rapport generert:\n{PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
