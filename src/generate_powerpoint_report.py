#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
KRISTIANSAND KOMMUNE - GENERATOR FOR POWERPOINT PRESENTASJON
===============================================================================
Genererer en 10-siders styringsrapport i 16:9 widescreen:
'reports/Kristiansand_EPM_Status_Prognose_Tiltaksrapport.pptx'
Inspirert av Framsikt-analysene i images/ (BoMiljø og Komskole),
med full status, prognoser, tiltak og månedlig tiltakseffekt mot Net Zero EOY.
===============================================================================
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

from config import REPORTS_DIR

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name in ["src", "powerbi"] else BASE_DIR
REPORTS_DIR = REPORTS_DIR
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PPTX_PATH = REPORTS_DIR / "Kristiansand_EPM_Status_Prognose_Tiltaksrapport.pptx"

# Fargepalett (Edward Tufte / Profesjonell Kommunal EPM)
COLOR_NAVY = RGBColor(15, 23, 42)      # #0F172A
COLOR_DARK_SLATE = RGBColor(30, 41, 59) # #1E293B
COLOR_MUTED_TEXT = RGBColor(100, 116, 139) # #64748B
COLOR_LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
COLOR_CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0
COLOR_BLUE_ACCENT = RGBColor(37, 99, 235)  # #2563EB
COLOR_ALERT_RED = RGBColor(220, 38, 38)    # #DC2626
COLOR_SUCCESS_GREEN = RGBColor(22, 163, 74) # #16A34A
COLOR_WHITE = RGBColor(255, 255, 255)

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide

    def add_header(slide, title_text, category_text="KRISTIANSAND KOMMUNE | ØKONOMISTYRING & EPM"):
        # Header banner text
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.9))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(9)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_BLUE_ACCENT
        
        p_tit = tf.add_paragraph()
        p_tit.text = title_text
        p_tit.font.size = Pt(20)
        p_tit.font.bold = True
        p_tit.font.color.rgb = COLOR_NAVY
        p_tit.space_before = Pt(3)

        # Thin separator line
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.02))
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_CARD_BORDER
        shape.line.fill.background()

    def add_card(slide, left, top, width, height, title, value, subtext="", alert=False, green=False):
        # Card background
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_LIGHT_BG
        shape.line.color.rgb = COLOR_ALERT_RED if alert else (COLOR_SUCCESS_GREEN if green else COLOR_CARD_BORDER)
        shape.line.width = Pt(1.5 if (alert or green) else 1)

        # Content
        tb = slide.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.12), Inches(width - 0.3), Inches(height - 0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = title.upper()
        p0.font.size = Pt(8.5)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_MUTED_TEXT

        p1 = tf.add_paragraph()
        p1.text = str(value)
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_ALERT_RED if alert else (COLOR_SUCCESS_GREEN if green else COLOR_NAVY)
        p1.space_before = Pt(2)

        if subtext:
            p2 = tf.add_paragraph()
            p2.text = subtext
            p2.font.size = Pt(8)
            p2.font.color.rgb = COLOR_MUTED_TEXT
            p2.space_before = Pt(2)

    # =========================================================================
    # SLIDE 1: TITTELSIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY
    bg1.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11.0), Inches(3.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "KRISTIANSAND KOMMUNE | ØKONOMI- OG VIRKSOMHETSSTYRING"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    p = tf1.add_paragraph()
    p.text = "Statusrapport 2. Tertial, Helårsprognoser og Tiltaksplan for Budsjettbalanse (Net Zero)"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(12)

    p = tf1.add_paragraph()
    p.text = "Diagnose, avviksdrivere og tiltaksprofil for Slettheia Bofellesskap og Mevold Grunnskole\nMål: Net Zero differanse mellom regnskap og budsjett per 31.12.2026"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_before = Pt(14)

    p = tf1.add_paragraph()
    p.text = "Utarbeidet av: Frank Ellingsen | Senior BI Specialist & Financial Controller\nBasert på data fra Visma Enterprise, Framsikt og Golden Record EPM Framework | Dato: Oktober 2026"
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(148, 163, 184)
    p.space_before = Pt(28)

    # =========================================================================
    # SLIDE 2: EXECUTIVE SUMMARY & KONSOLIDERT BILDE
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Executive Summary: Samlet Avviksbilde og Veien til Balanse (Net Zero)")

    # 4 Nøkkelkort
    add_card(s2, 0.8, 1.6, 2.7, 1.1, "YTD Regnskap (T2)", "31,52 mill. kr", "Faktisk bokført Jan–Aug")
    add_card(s2, 3.8, 1.6, 2.7, 1.1, "YTD Budsjett (T2)", "29,30 mill. kr", "Akkumulert T2-ramme")
    add_card(s2, 6.8, 1.6, 2.7, 1.1, "Akkumulert Merforbruk", "-2,23 mill. kr", "Avvik: -7,6 % (Kritisk)", alert=True)
    add_card(s2, 9.8, 1.6, 2.7, 1.1, "Net Zero Mål 31.12", "0,00 kr", "Full budsjettbalanse", green=True)

    # Hovedtabell
    rows_s2 = [
        ["Enhet / Område", "YTD Budsjett", "YTD Regnskap", "YTD Avvik", "Avvik %", "EOY Uendret Drift", "Tiltak T3 (Sept-Des)", "EOY Balansert"],
        ["Slettheia Bofellesskap (Helse)", "11 337 237 kr", "12 622 851 kr", "-1 285 614 kr", "-11,3 %", "19 162 112 kr", "+1 928 421 kr", "17 233 691 kr (0 kr)"],
        ["Mevold Grunnskole (Oppvekst)", "17 958 000 kr", "18 902 000 kr", "-944 000 kr", "-5,3 %", "28 353 000 kr", "+1 416 000 kr", "27 490 000 kr (0 kr)"],
        ["TOTALT KONSOLIDERT", "29 295 237 kr", "31 524 851 kr", "-2 229 614 kr", "-7,6 %", "47 515 112 kr", "+3 344 421 kr", "44 723 691 kr (0 kr)"]
    ]

    t_shape = s2.shapes.add_table(len(rows_s2), len(rows_s2[0]), Inches(0.8), Inches(3.0), Inches(11.733), Inches(1.8))
    table = t_shape.table
    table.columns[0].width = Inches(3.0)
    for i in range(1, len(rows_s2[0])):
        table.columns[i].width = Inches(1.24)

    for r_idx, row in enumerate(rows_s2):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9)
            p.font.name = "Segoe UI"
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_NAVY
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
            elif r_idx == len(rows_s2) - 1:
                p.font.bold = True
                p.font.color.rgb = COLOR_NAVY
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            else:
                p.font.color.rgb = COLOR_DARK_SLATE
            
            p.alignment = PP_ALIGN.RIGHT if c_idx > 0 else PP_ALIGN.LEFT
            if c_idx == 3 and r_idx > 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_ALERT_RED

    # Diagnostisk tekstboks nederst
    tb = s2.shapes.add_textbox(Inches(0.8), Inches(5.1), Inches(11.733), Inches(1.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "STRATEGISK OPPFORDRING & BESLUTNINGSGRUNNLAG:"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    points = [
        "1. Uendret drift vil gi et samlet underskudd på -3,34 mill. kr ved årsslutt, noe som utløser formell varslingsplikt til Bystyret jf. Kommuneloven § 14-5.",
        "2. Årsakene er strukturelle og operasjonelle: Slettheia Bofellesskap er tynget av eksterne vikarbyråer og turnusovertid, mens Mevold Grunnskole har lærervikarmerforbruk.",
        "3. Løsningen er en forpliktende tiltaksplan i T3 (september-desember) med månedlig sparing på totalt 3,34 mill. kr mot run-rate trend for å sikre Net Zero i årsavvik."
    ]
    for pt in points:
        p = tf.add_paragraph()
        p.text = pt
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_MUTED_TEXT
        p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 3: BOMILJØ - STATUS OG AVVIKSANALYSE (FRAMSIKT VIEW)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Slettheia Bofellesskap: Status og Avviksanalyse Jan–Aug 2026")

    # Kort
    add_card(s3, 0.8, 1.6, 2.7, 1.1, "Budsjett YTD (Aug)", "11,34 mill. kr", "11 337 125 kr")
    add_card(s3, 3.8, 1.6, 2.7, 1.1, "Regnskap YTD (Aug)", "12,63 mill. kr", "12 630 912 kr")
    add_card(s3, 6.8, 1.6, 2.7, 1.1, "Avvik YTD (Framsikt)", "-1,29 mill. kr", "-11,4 % overforbruk", alert=True)
    add_card(s3, 9.8, 1.6, 2.7, 1.1, "Siste Måned (August)", "-240 662 kr", "Regnskap: 1,77M | Budsjett: 1,53M", alert=True)

    # Venstre tabell: Månedlig avviksutvikling
    mnd_data = [
        ["Måned", "Budsjett", "Regnskap", "Avvik", "Kommentar / Status"],
        ["Januar", "1 403 337 kr", "1 014 752 kr", "+388 585 kr", "Mindreforbruk (positiv start)"],
        ["Februar", "1 410 893 kr", "2 082 090 kr", "-671 197 kr", "🚨 Februarsjokk: Vikarbølge & overtid"],
        ["Mars", "1 342 381 kr", "1 541 249 kr", "-198 868 kr", "Høyt sykefravær og vikarbruk"],
        ["April", "2 357 359 kr", "2 256 716 kr", "+100 643 kr", "Feriepengejustering / avstemming"],
        ["Mai", "1 544 215 kr", "1 613 437 kr", "-69 222 kr", "Stabilt merforbruk"],
        ["Juni", "241 681 kr", "519 336 kr", "-277 655 kr", "Ferieoppstart, sommervikarer"],
        ["Juli", "1 512 209 kr", "1 837 523 kr", "-325 314 kr", "Sommerturnus & byråinnleie"],
        ["August", "1 525 162 kr", "1 765 810 kr", "-240 648 kr", "Fortsatt høyt vikarpress"],
        ["YTD SUM", "11 337 237 kr", "12 622 851 kr", "-1 285 614 kr", "Akkumulert merforbruk T2"]
    ]
    t_mnd = s3.shapes.add_table(len(mnd_data), len(mnd_data[0]), Inches(0.8), Inches(3.0), Inches(6.5), Inches(3.8))
    t_mnd.table.columns[0].width = Inches(1.1)
    t_mnd.table.columns[1].width = Inches(1.2)
    t_mnd.table.columns[2].width = Inches(1.2)
    t_mnd.table.columns[3].width = Inches(1.1)
    t_mnd.table.columns[4].width = Inches(1.9)
    for r_idx, row in enumerate(mnd_data):
        for c_idx, val in enumerate(row):
            cell = t_mnd.table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8)
            p.font.name = "Segoe UI"
            if r_idx == 0:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
            elif r_idx == len(mnd_data) - 1:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            if c_idx in [1, 2, 3]:
                p.alignment = PP_ALIGN.RIGHT
            if c_idx == 3 and "-" in val:
                p.font.color.rgb = COLOR_ALERT_RED

    # Høyre boks: Lønn funn og hovedårsaker
    box_r = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(3.0), Inches(4.933), Inches(3.8))
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = COLOR_LIGHT_BG
    box_r.line.color.rgb = COLOR_CARD_BORDER
    tf_r = box_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "DIAGNOSTISKE FUNN (FRAMSIKT ANALYSE):"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    insights = [
        "1. Dekomponering av Avvik (-1,29 MNOK):",
        "   • 1 Lønn: -1 149 674 kr (-89 % av totalavviket)",
        "   • 2 Utgifter (Drift): -144 113 kr (-11 %)",
        "2. Februaranomalien (-671 kNOK):",
        "   • Ekstremt høyt fravær og influensatopp utløste samtidig bruk av eksterne vikarbyråer og intern overtid for å dekke lovpålagt 2:1-bemanning.",
        "3. Topp Overforbrukskontoer:",
        "   • Art 101000 Fastlønn ordinære: -474 918 kr",
        "   • Art 127040 Kjøp av vikarbyrå: -382 656 kr",
        "   • Art 102031 Vikar kveld/natt: -259 303 kr",
        "   • Art 104000 Overtidslønn: -185 573 kr",
        "   • Art 103000 Ekstrahjelp: -141 648 kr",
        "4. Positive Motposter:",
        "   • Art 102002 Foreldrepermisjon vikar: +189 928 kr",
        "   • Art 112098 Lærlingtilskudd: +160 447 kr"
    ]
    for ins in insights:
        p = tf_r.add_paragraph()
        p.text = ins
        p.font.size = Pt(8.5)
        p.font.color.rgb = COLOR_DARK_SLATE
        p.space_before = Pt(3)

    # =========================================================================
    # SLIDE 4: BOMILJØ - HELÅRSPROGNOSE & VEIEN TIL NET ZERO
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Slettheia Bofellesskap: Helårsprognose og Nødvendig Tiltaksbane")

    add_card(s4, 0.8, 1.6, 2.7, 1.1, "Vedtatt Årsbudsjett", "17,23 mill. kr", "Bystyrets vedtatte ramme")
    add_card(s4, 3.8, 1.6, 2.7, 1.1, "EOY Run-Rate Prognose", "19,16 mill. kr", "Fremskriving uten tiltak", alert=True)
    add_card(s4, 6.8, 1.6, 2.7, 1.1, "Forventet EOY Merforbruk", "-1,93 mill. kr", "Uavbøtt avvik ved årsslutt", alert=True)
    add_card(s4, 9.8, 1.6, 2.7, 1.1, "Målscenario etter Tiltak", "17,23 mill. kr", "Avvik: 0 kr (Net Zero)", green=True)

    # Tabell over tiltak for BoMiljø
    tiltak_bom = [
        ["ID", "Tiltaksbeskrivelse", "KOSTRA-Art", "Ansvarlig", "Mnd Effekt", "Total Effekt T3", "Forankring"],
        ["B1", "Totalstopp for eksterne vikarbyråer (Adecco/Dedicate)", "127040", "Enhetsleder", "125 000 kr/mnd", "500 000 kr", "Avtale m/ intern vikarpool"],
        ["B2", "Turnusomlegging & forhåndsavtalt helgedekning", "102030/31", "Avdelingsleder", "110 000 kr/mnd", "440 000 kr", "Samarbeid m/ tillitsvalgte"],
        ["B3", "Restriktiv overtidskontroll & ledergodkjenning", "104000", "Enhetsleder", "95 000 kr/mnd", "380 000 kr", "Digital timeregistrering"],
        ["B4", "Intensivert sykefraværsoppfølging & NAV-refusjoner", "102000/1690", "HR-konsulent", "100 000 kr/mnd", "400 000 kr", "Aktiv IA-oppfølging"],
        ["B5", "Søknad om toppfinansiering ressurskrevende tjenester", "170000", "Kommunalsjef", "Engangsbeløp", "208 421 kr", "Vedtak 2:1-beboere"],
        ["SUM", "SAMLET TILTAKSEFFEKT SLETHEIA BOFELLESSKAP (T3)", "Flere", "Enhetsleder/Stab", "-", "1 928 421 kr", "Lederavtale signert"]
    ]
    t_tb = s4.shapes.add_table(len(tiltak_bom), len(tiltak_bom[0]), Inches(0.8), Inches(3.0), Inches(11.733), Inches(3.8))
    t_tb.table.columns[0].width = Inches(0.6)
    t_tb.table.columns[1].width = Inches(3.5)
    t_tb.table.columns[2].width = Inches(1.1)
    t_tb.table.columns[3].width = Inches(1.4)
    t_tb.table.columns[4].width = Inches(1.4)
    t_tb.table.columns[5].width = Inches(1.5)
    t_tb.table.columns[6].width = Inches(2.233)
    for r_idx, row in enumerate(tiltak_bom):
        for c_idx, val in enumerate(row):
            cell = t_tb.table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8.5)
            p.font.name = "Segoe UI"
            if r_idx == 0:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
            elif r_idx == len(tiltak_bom) - 1:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(240, 253, 244)
                p.font.color.rgb = COLOR_SUCCESS_GREEN
            if c_idx in [4, 5]:
                p.alignment = PP_ALIGN.RIGHT

    # =========================================================================
    # SLIDE 5: BOMILJØ - MÅNEDLIG EFFEKTPROFIL SEPT-DES (NET ZERO LUKKING)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Slettheia Bofellesskap: Månedlig Balanseringsprofil Sept–Des")

    add_card(s5, 0.8, 1.6, 3.6, 1.1, "Akkumulert Merforbruk T2", "-1 285 614 kr", "Historisk per 31.08.2026", alert=True)
    add_card(s5, 4.8, 1.6, 3.6, 1.1, "Budsjettramme T3 (Sept-Des)", "5 896 454 kr", "Maksimalt tillatt forbruk: 4 610 840 kr")
    add_card(s5, 8.8, 1.6, 3.733, 1.1, "Helårsresultat 31.12", "0 kr i avvik", "Net Zero budsjettbalanse", green=True)

    # Tabell over månedlig utvikling Sept-Des
    bal_data = [
        ["Periode / Måned", "Opprinnelig Budsjett", "Run-Rate Fremskriving", "Planlagte Tiltak", "Justert Regnskap", "Akkumulert Avvik"],
        ["Januar - August (T2)", "11 337 237 kr", "12 622 851 kr", "0 kr", "12 622 851 kr", "-1 285 614 kr"],
        ["September", "1 504 399 kr", "1 665 101 kr", "+430 000 kr", "1 235 101 kr", "-1 016 316 kr"],
        ["Oktober", "1 418 774 kr", "1 579 476 kr", "+430 000 kr", "1 149 476 kr", "-747 018 kr"],
        ["November", "1 418 540 kr", "1 579 242 kr", "+430 000 kr", "1 149 242 kr", "-477 720 kr"],
        ["Desember", "1 554 741 kr", "1 715 443 kr", "+638 421 kr", "1 077 022 kr", "0 kr (I BALANSE)"],
        ["HELÅR TOTALT", "17 233 691 kr", "19 162 112 kr", "+1 928 421 kr", "17 233 691 kr", "0 kr (NET ZERO)"]
    ]
    t_bal = s5.shapes.add_table(len(bal_data), len(bal_data[0]), Inches(0.8), Inches(3.0), Inches(11.733), Inches(3.8))
    t_bal.table.columns[0].width = Inches(2.2)
    t_bal.table.columns[1].width = Inches(1.9)
    t_bal.table.columns[2].width = Inches(1.9)
    t_bal.table.columns[3].width = Inches(1.6)
    t_bal.table.columns[4].width = Inches(1.9)
    t_bal.table.columns[5].width = Inches(2.233)
    for r_idx, row in enumerate(bal_data):
        for c_idx, val in enumerate(row):
            cell = t_bal.table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8.5)
            p.font.name = "Segoe UI"
            if r_idx == 0:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
            elif r_idx == len(bal_data) - 1:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(240, 253, 244)
                p.font.color.rgb = COLOR_SUCCESS_GREEN
            if c_idx > 0:
                p.alignment = PP_ALIGN.RIGHT
            if c_idx == 3 and "+" in val:
                p.font.color.rgb = COLOR_SUCCESS_GREEN
            if c_idx == 5 and "0 kr" in val:
                p.font.bold = True
                p.font.color.rgb = COLOR_SUCCESS_GREEN

    # =========================================================================
    # SLIDE 6: KOMSKOLE - STATUS OG ENHETSFORDELING (FRAMSIKT VIEW)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Mevold Grunnskole: Status og Enhetsfordeling 2. Tertial 2026")

    add_card(s6, 0.8, 1.6, 2.7, 1.1, "Budsjett hiå (T2)", "17,96 mill. kr", "17 958 000 kr")
    add_card(s6, 3.8, 1.6, 2.7, 1.1, "Regnskap hiå (T2)", "18,90 mill. kr", "18 902 000 kr")
    add_card(s6, 6.8, 1.6, 2.7, 1.1, "Avvik hiå", "-944 000 kr", "-5,3 % overforbruk", alert=True)
    add_card(s6, 9.8, 1.6, 2.7, 1.1, "Årsbudsjett", "27,49 mill. kr", "Forbrukt hiå: 68,8 %")

    # Matrisetabell (Inspirert av skole_framsikt_cond_format.png)
    skole_matrise = [
        ["Enhet (brukt)", "Regnskap hiå", "Budsjett hiå", "Avvik i kr", "Avvik %", "Årsbudsjett", "Brukt hiå %", "Status"],
        ["Ordinær undervisning", "12 024 000 kr", "11 385 000 kr", "-639 000 kr", "-5,6 %", "17 590 000 kr", "68,4 %", "🚩 Merforbruk"],
        ["Spesialundervisning grunnskole", "2 792 000 kr", "2 496 000 kr", "-296 000 kr", "-11,9 %", "4 114 000 kr", "67,9 %", "🚩 Merforbruk"],
        ["Grunnskole (felles)", "1 733 000 kr", "1 761 000 kr", "+28 000 kr", "+1,6 %", "2 919 000 kr", "59,4 %", "✓ Under ramme"],
        ["Skolefritidstilbud (SFO)", "983 000 kr", "813 000 kr", "-170 000 kr", "-20,9 %", "1 233 000 kr", "79,7 %", "🚩 Merforbruk"],
        ["Voksenopplæring", "491 000 kr", "513 000 kr", "+22 000 kr", "+4,3 %", "35 000 kr", "1402,9 %", "Avstemmes"],
        ["Skoleskyss", "469 000 kr", "516 000 kr", "+47 000 kr", "+9,1 %", "775 000 kr", "60,5 %", "✓ Under ramme"],
        ["PPT (Pedagogisk-psykologisk)", "286 000 kr", "350 000 kr", "+64 000 kr", "+18,3 %", "700 000 kr", "40,9 %", "✓ Under ramme"],
        ["Ekskursjonar / Leirskule", "124 000 kr", "124 000 kr", "0 kr", "0,0 %", "124 000 kr", "100,0 %", "I balanse"],
        ["TOTALT MEVOLD SKOLE", "18 902 000 kr", "17 958 000 kr", "-944 000 kr", "-5,3 %", "27 490 000 kr", "68,8 %", "🚩 Totalt avvik"]
    ]
    t_sk = s6.shapes.add_table(len(skole_matrise), len(skole_matrise[0]), Inches(0.8), Inches(3.0), Inches(11.733), Inches(3.8))
    t_sk.table.columns[0].width = Inches(2.7)
    t_sk.table.columns[1].width = Inches(1.3)
    t_sk.table.columns[2].width = Inches(1.3)
    t_sk.table.columns[3].width = Inches(1.2)
    t_sk.table.columns[4].width = Inches(1.0)
    t_sk.table.columns[5].width = Inches(1.4)
    t_sk.table.columns[6].width = Inches(1.1)
    t_sk.table.columns[7].width = Inches(1.733)
    for r_idx, row in enumerate(skole_matrise):
        for c_idx, val in enumerate(row):
            cell = t_sk.table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8.5)
            p.font.name = "Segoe UI"
            if r_idx == 0:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
            elif r_idx == len(skole_matrise) - 1:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            if c_idx in [1, 2, 3, 4, 5, 6]:
                p.alignment = PP_ALIGN.RIGHT
            if c_idx == 3 and "-" in val:
                p.font.color.rgb = COLOR_ALERT_RED

    # =========================================================================
    # SLIDE 7: KOMSKOLE - KONTOTYPE & REFUSJONSDYPDYKK
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Mevold Grunnskole: Kontotype- og Refusjonsanalyse (Framsikt)")

    # Venstre boks: Kontotype avvik
    box_l = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.2))
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = COLOR_LIGHT_BG
    box_l.line.color.rgb = COLOR_CARD_BORDER
    tf_l = box_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "KONTOTYPE FORDELING (AVVIK I TUSEN KR):"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    k_items = [
        ("Lønn (totalt)", "-1 302 kNOK", "Hovedkilde til overforbruk"),
        ("Overføringsutgifter", "-262 kNOK", "Mva og fylkeskommunale betalinger"),
        ("Finansutgifter", "-250 kNOK", "Avsetninger til bundne fond"),
        ("Finansinntekter", "-142 kNOK", "Bruk av bundne driftsfond"),
        ("Kjøp av varer og tjenester", "-41 kNOK", "IKT, læremidler og forbruk"),
        ("Overføringsinntekter", "+176 kNOK", "Statstilskudd og refusjoner"),
        ("Kjøp av prod. / Salg varer", "+611 kNOK", "Refusjoner og annet salg"),
        ("NETTO AVVIK HELE ENHETEN", "-944 kNOK", "Samlet overforbruk per T2")
    ]
    for tit, val, desc in k_items:
        p = tf_l.add_paragraph()
        p.text = f"• {tit}: {val} ({desc})"
        p.font.size = Pt(8.5)
        p.font.color.rgb = COLOR_ALERT_RED if "-" in val else (COLOR_SUCCESS_GREEN if "+" in val else COLOR_NAVY)
        p.space_before = Pt(6)

    # Høyre boks: Topp positive og negative enkeltkontoer
    box_r7 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.733), Inches(5.2))
    box_r7.fill.solid()
    box_r7.fill.fore_color.rgb = COLOR_LIGHT_BG
    box_r7.line.color.rgb = COLOR_CARD_BORDER
    tf_r7 = box_r7.text_frame
    tf_r7.word_wrap = True
    p = tf_r7.paragraphs[0]
    p.text = "TOPP DRIVERE: NEGATIVE VS POSITIVE KONTOER:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_NAVY

    acc_items = [
        "🚨 TOPP NEGATIVE KONTOER (MERFORBRUK):",
        "  1. Fast lønn lærere: -1 436 000 kr (Strukturelt lønnspress)",
        "  2. Lønn til vikarer: -381 000 kr (Kortsiktig vikarbruk)",
        "  3. Sykevikarer: -272 000 kr (Høyt legemeldt fravær)",
        "  4. Overtidslønn: -230 000 kr (Mangel på faglærere)",
        "  5. Lønn ekstrahjelp: -123 000 kr (Spesialundervisning/SFO)",
        "",
        "✓ TOPP POSITIVE KONTOER (REFUSJONER / INNSPARINGER):",
        "  1. Refusjon av fødselspenger: +979 000 kr (NAV-innbetaling)",
        "  2. Sykelønnsrefusjon: +449 000 kr (Refusjon fra NAV)",
        "  3. Kompensasjon moms drift: +266 000 kr",
        "  4. Refusjon fra fylkeskommuner: +250 000 kr",
        "  5. Refusjon fra NAV (andre): +222 000 kr",
        "",
        "KONKLUSJON: Skolen redder deler av læreroverforbruket gjennom ekstraordinære fødselspenger og refusjoner, men lønnsdriften må strammes inn i T3."
    ]
    for it in acc_items:
        p = tf_r7.add_paragraph()
        p.text = it
        p.font.size = Pt(8)
        p.font.color.rgb = COLOR_DARK_SLATE
        p.space_before = Pt(2)

    # =========================================================================
    # SLIDE 8: KOMSKOLE - TILTAKSPLAN & VEIEN TIL NET ZERO
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Mevold Grunnskole: Helårsprognose og Tiltaksplan for Net Zero")

    add_card(s8, 0.8, 1.6, 2.7, 1.1, "Vedtatt Årsbudsjett", "27,49 mill. kr", "27 490 000 kr")
    add_card(s8, 3.8, 1.6, 2.7, 1.1, "EOY Run-Rate Prognose", "28,35 mill. kr", "Uendret drift (sprekk)", alert=True)
    add_card(s8, 6.8, 1.6, 2.7, 1.1, "Uavbøtt Avvik EOY", "-863 000 kr", "Sprekk mot årsbudsjett", alert=True)
    add_card(s8, 9.8, 1.6, 2.7, 1.1, "Målscenario etter Tiltak", "27,49 mill. kr", "Avvik: 0 kr (Net Zero)", green=True)

    # Tiltakstabell for Skolen
    tiltak_skole = [
        ["ID", "Tiltaksbeskrivelse", "Område / Art", "Ansvarlig", "Mnd Effekt", "Total Effekt T3", "Forankring"],
        ["S1", "Stopp i eksterne lærervikarer; intern omdisponering", "Undervisning / 1020", "Rektor", "125 000 kr/mnd", "500 000 kr", "Fagledermøte"],
        ["S2", "Timeplanoptimalisering & stans i ekstrahjelp", "Ordinær / 1030", "Inspektør", "75 000 kr/mnd", "300 000 kr", "Timeplanlegger"],
        ["S3", "Innkjøpsstopp for IKT-utstyr, lærebøker & forbruk", "Drift / 1110-1200", "Rektor", "50 000 kr/mnd", "200 000 kr", "Full innkjøpsfrys"],
        ["S4", "Full avstemming og purring av NAV sykelønnsrefusjon", "Refusjon / 1690", "Skolesekretær/HR", "Aktiv purring", "250 000 kr", "Altinn/NAV avstemt"],
        ["S5", "Samordning av spesialpedagogiske timer på tvers av trinn", "Spes.und / 1010", "Avdelingsleder", "41 500 kr/mnd", "166 000 kr", "PPT samråd"],
        ["SUM", "SAMLET TILTAKSEFFEKT MEVOLD GRUNNSKOLE (T3)", "Flere", "Rektor / Ledergruppe", "-", "1 416 000 kr", "Vedtak iverksatt"]
    ]
    t_tsk = s8.shapes.add_table(len(tiltak_skole), len(tiltak_skole[0]), Inches(0.8), Inches(3.0), Inches(11.733), Inches(3.8))
    t_tsk.table.columns[0].width = Inches(0.6)
    t_tsk.table.columns[1].width = Inches(3.5)
    t_tsk.table.columns[2].width = Inches(1.3)
    t_tsk.table.columns[3].width = Inches(1.3)
    t_tsk.table.columns[4].width = Inches(1.4)
    t_tsk.table.columns[5].width = Inches(1.5)
    t_tsk.table.columns[6].width = Inches(2.133)
    for r_idx, row in enumerate(tiltak_skole):
        for c_idx, val in enumerate(row):
            cell = t_tsk.table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8.5)
            p.font.name = "Segoe UI"
            if r_idx == 0:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
            elif r_idx == len(tiltak_skole) - 1:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(240, 253, 244)
                p.font.color.rgb = COLOR_SUCCESS_GREEN
            if c_idx in [4, 5]:
                p.alignment = PP_ALIGN.RIGHT

    # =========================================================================
    # SLIDE 9: KONSOLIDERT TILTAKSMATRISE & NET ZERO REGNSKAPSAVSLUTNING
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Konsolidert Tiltaksmatrise & Net Zero Regnskapsavslutning 31.12")

    add_card(s9, 0.8, 1.6, 2.7, 1.1, "Samlet Årsbudsjett", "44,72 mill. kr", "Slettheia + Mevold")
    add_card(s9, 3.8, 1.6, 2.7, 1.1, "Run-Rate EOY (Før tiltak)", "47,52 mill. kr", "-3,34 mill. kr merforbruk", alert=True)
    add_card(s9, 6.8, 1.6, 2.7, 1.1, "Samlet Tiltakspakke", "+3,34 mill. kr", "Realisering Sept–Des", green=True)
    add_card(s9, 9.8, 1.6, 2.7, 1.1, "SLUTTRESULTAT 31.12", "0,00 kr", "Eksakt Net Zero balanse", green=True)

    # Master Tabell
    kons_data = [
        ["Hovedpost / Tiltakskategori", "Slettheia Bofellesskap", "Mevold Grunnskole", "Samlet Effekt T3", "Månedlig Takt (Sept-Des)", "Garantist / Kontroll"],
        ["1. Vikarrestriksjoner & Stopp i Eksterne Byråer", "500 000 kr", "500 000 kr", "1 000 000 kr", "250 000 kr / mnd", "Enhetsledere / HR"],
        ["2. Turnusomlegging, Overtidsstopp & Timeplanoptimalisering", "820 000 kr", "300 000 kr", "1 120 000 kr", "280 000 kr / mnd", "Avdelingsledere / Tillitsvalgte"],
        ["3. Driftsreduksjon & Full Innkjøpsfrys (IKT/materiell)", "0 kr", "200 000 kr", "200 000 kr", "50 000 kr / mnd", "Økonomiavdelingen"],
        ["4. Intensivert NAV Refusjonsavstemming (Sykepenger/IA)", "400 000 kr", "250 000 kr", "650 000 kr", "Løpende purring Altinn", "Lønnsavdelingen"],
        ["5. Tilleggsfinansiering / Ressurskrevende Tjenester", "208 421 kr", "166 000 kr", "374 421 kr", "Søknad / Vedtaksjustering", "Kommunalsjef / Stat"],
        ["TOTALT INNSPART I 3. TERTIAL", "1 928 421 kr", "1 416 000 kr", "3 344 421 kr", "836 105 kr / mnd", "Periodisk månedsrapport"],
        ["ÅRSBUDSJETT", "17 233 691 kr", "27 490 000 kr", "44 723 691 kr", "-", "Vedtatt av Bystyret"],
        ["FORVENTET REGNSKAP MED TILTAK", "17 233 691 kr", "27 490 000 kr", "44 723 691 kr", "-", "Revidert årsregnskap"],
        ["SLUTTAVVIK PER 31.12.2026", "0 kr (0,0 %)", "0 kr (0,0 %)", "0 kr (0,0 %)", "-", "NET ZERO OPPNÅDD ✓"]
    ]
    t_k = s9.shapes.add_table(len(kons_data), len(kons_data[0]), Inches(0.8), Inches(3.0), Inches(11.733), Inches(3.8))
    t_k.table.columns[0].width = Inches(3.6)
    t_k.table.columns[1].width = Inches(1.6)
    t_k.table.columns[2].width = Inches(1.6)
    t_k.table.columns[3].width = Inches(1.6)
    t_k.table.columns[4].width = Inches(1.8)
    t_k.table.columns[5].width = Inches(1.533)
    for r_idx, row in enumerate(kons_data):
        for c_idx, val in enumerate(row):
            cell = t_k.table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(8)
            p.font.name = "Segoe UI"
            if r_idx == 0:
                p.font.bold = True
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
            elif r_idx >= len(kons_data) - 4:
                p.font.bold = True
                if r_idx == len(kons_data) - 1:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(240, 253, 244)
                    p.font.color.rgb = COLOR_SUCCESS_GREEN
                else:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
            if c_idx in [1, 2, 3, 4]:
                p.alignment = PP_ALIGN.RIGHT

    # =========================================================================
    # SLIDE 10: HUMAN-IN-THE-LOOP, JURIDISK RAMME & IMPLEMENTERING
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Ledelsesforankring, Human-in-the-Loop & Kommuneloven § 14-5")

    # 3 Kolonner / Steg for implementering
    col_w = 3.64
    steps = [
        ("1. HUMAN-IN-THE-LOOP (HITL)", [
            "• Streamlit Portal:",
            "  Enhetsledere logger på lokalt webpanel og gjennomgår AI-genererte tiltaksforslag.",
            "• Glass-Box Transparens:",
            "  Ingen automatiske budsjettkutt. Menneskelig saksbehandler må aktivt godkjenne (GODKJENT / ENDRET / AVVIST).",
            "• Tjenstlig Begrunnelse:",
            "  Obligatorisk tekstfelt for faglig vurdering av forsvarlighet i tjenestetilbudet."
        ]),
        ("2. JURIDISK ETTERLEVELSE", [
            "• Kommuneloven § 14-5:",
            "  Plikt til å iverksette korrigerende tiltak umiddelbart ved vesentlige budsjettavvik.",
            "• EU AI Act Art. 27:",
            "  Full sporbarhet for beslutningsstøttesystemer i offentlig sektor.",
            "• Revisjonsspor i SQLite:",
            "  Hver handling skrives direkte til 'Audit_AI_Actions' med tidsstempel, bruker-ID, konfidensscore og IP-adresse."
        ]),
        ("3. FREMDRIFT & OPPFØLGING", [
            "• Månedlig Avstemming:",
            "  Økonomiavdelingen avstemmer faktisk utfall mot tiltaksprofilen den 10. i hver måned.",
            "• Varsling ved Glipp:",
            "  Dersom tiltakseffekten svikter med > 50 000 kr i en måned, trigges varsel til kommunalsjef.",
            "• Årsavslutning 2026:",
            "  Revisjonsgodkjent regnskap avsluttes i full balanse med Net Zero avvik."
        ])
    ]

    for idx, (st_tit, bullets) in enumerate(steps):
        l = 0.8 + idx * (col_w + 0.4)
        box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(1.8), Inches(col_w), Inches(4.9))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_LIGHT_BG
        box.line.color.rgb = COLOR_CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = st_tit
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE_ACCENT

        for b in bullets:
            p = tf.add_paragraph()
            p.text = b
            p.font.size = Pt(8.5)
            p.font.color.rgb = COLOR_NAVY if b.startswith("•") else COLOR_MUTED_TEXT
            p.font.bold = True if b.startswith("•") else False
            p.space_before = Pt(4)

    prs.save(str(PPTX_PATH))
    print(f"[OK] Fullstendig PowerPoint-rapport generert:\n{PPTX_PATH}")

if __name__ == "__main__":
    create_deck()
