#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
KRISTIANSAND KOMMUNE - GENERATOR FOR EPM OG FRAMSIKT GRAFER
===============================================================================
Genererer 3 profesjonelle grafer i henhold til Edward Tuftes Data-Ink standarder:
1. 'reports/chart_bomiljo_monthly.png': Månedlig utvikling og Net Zero tiltaksbane (Jan-Des).
2. 'reports/chart_komskole_units.png': Horisontale avvik per enhet for Mevold Skole.
3. 'reports/chart_netzero_waterfall.png': Vannfallsdiagram fra Run-Rate sprekk til Net Zero balanse.
===============================================================================
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import numpy as np

from config import REPORTS_DIR

# Konfigurer matplotlib for headless og UTF-8
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#F1F5F9'
plt.rcParams['grid.linestyle'] = '--'

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name in ["src", "powerbi"] else BASE_DIR
REPORTS_DIR = REPORTS_DIR
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_charts():
    # -------------------------------------------------------------------------
    # 1. BOMILJØ: MÅNEDLIG UTVIKLING OG TILTROSKORRIDOR (Jan - Des)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des']
    budget = [1.40, 1.41, 1.34, 2.36, 1.54, 0.24, 1.51, 1.53, 1.50, 1.42, 1.42, 1.55] # mill kr
    actuals = [1.01, 2.08, 1.54, 2.26, 1.61, 0.52, 1.84, 1.77] # Jan - Aug
    run_rate = [np.nan]*7 + [1.77, 1.67, 1.58, 1.58, 1.72] # Sept - Des uendret drift
    with_actions = [np.nan]*7 + [1.77, 1.24, 1.15, 1.15, 1.08] # Sept - Des med tiltak
    
    x = np.arange(len(months))
    
    # Budsjettlinje
    ax.plot(x, budget, label='Budsjett (Vedtatt ramme)', color='#64748B', linestyle='--', linewidth=1.5)
    
    # Faktisk regnskap Jan-Aug
    ax.plot(x[:8], actuals, label='Faktisk Regnskap YTD', color='#0F172A', linewidth=2.2, marker='o', markersize=5)
    
    # Februaranomali markering
    ax.annotate('Februarsjokk: Vikarbølge\nog overtid (2,08 mill)', xy=(1, 2.08), xytext=(1.2, 2.25),
                arrowprops=dict(facecolor='#DC2626', shrink=0.08, width=1, headwidth=5),
                fontsize=8, fontweight='bold', color='#DC2626')

    # Run-rate fremskriving uten tiltak
    ax.plot(x[7:], run_rate[7:], label='Run-Rate Prognose (Uendret drift: -1,93 mill)', color='#DC2626', linestyle=':', linewidth=1.8, marker='s', markersize=4)

    # Tiltaksbane til Net Zero
    ax.plot(x[7:], with_actions[7:], label='Net Zero Tiltaksbane (Regnskap = Budsjett: 0 kr)', color='#16A34A', linewidth=2.0, marker='^', markersize=5)
    
    # Fyllområde som viser innsparingseffekten
    ax.fill_between(x[7:], with_actions[7:], run_rate[7:], color='#DCFCE7', alpha=0.5, label='Realisert tiltakseffekt (1,93 mill)')

    ax.set_title('Slettheia Bofellesskap: Månedlig Forløp, Februarsjokk og Net Zero Tiltaksbane (mill. kr)', fontsize=11, fontweight='bold', color='#0F172A', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=9)
    ax.set_ylabel('Kostnad (mill. kr)', fontsize=9, color='#475569')
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Tufte minimalisme: Fjern topp- og høyrelinjer
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#E2E8F0', fontsize=8, loc='upper right')
    
    plt.tight_layout()
    chart1_path = REPORTS_DIR / "chart_bomiljo_monthly.png"
    plt.savefig(chart1_path)
    plt.close()
    print(f"[OK] Graf 1 lagret: {chart1_path}")

    # -------------------------------------------------------------------------
    # 2. KOMSKOLE: HORISONTALE AVVIK PER ENHET (Inspirert av skole1 / skole2)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    
    units = [
        'Ordinær undervisning',
        'Spesialundervisning',
        'Skolefritidstilbud (SFO)',
        'Voksenopplæring',
        'Grunnskole felles',
        'Skoleskyss',
        'PPT-tjeneste'
    ]
    variances = [-639, -296, -170, 22, 28, 47, 64] # tusen kr
    colors = ['#DC2626' if v < 0 else '#16A34A' for v in variances]
    
    y = np.arange(len(units))
    bars = ax.barh(y, variances, color=colors, height=0.55)
    
    ax.axvline(0, color='#0F172A', linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(units, fontsize=9, fontweight='medium')
    ax.set_xlabel('Avvik YTD 2. Tertial (tusen kr) — Negativt = Overforbruk', fontsize=9, color='#475569')
    ax.set_title('Mevold Grunnskole: Avvik per Enhet per 2. Tertial (tusen kr)', fontsize=11, fontweight='bold', color='#0F172A', pad=12)
    
    # Direkte merking på stolpene (Tufte-prinsipp)
    for bar, val in zip(bars, variances):
        xval = bar.get_width()
        align = 'right' if xval < 0 else 'left'
        offset = -15 if xval < 0 else 8
        ax.annotate(f"{val:+d} k",
                    xy=(xval, bar.get_y() + bar.get_height() / 2),
                    xytext=(offset, 0),
                    textcoords="offset points",
                    ha=align, va='center',
                    fontsize=8.5, fontweight='bold',
                    color='#DC2626' if val < 0 else '#16A34A')
        
    ax.set_xlim(-750, 150)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    chart2_path = REPORTS_DIR / "chart_komskole_units.png"
    plt.savefig(chart2_path)
    plt.close()
    print(f"[OK] Graf 2 lagret: {chart2_path}")

    # -------------------------------------------------------------------------
    # 3. KONSOLIDERT VANNFALLSDIAGRAM TIL NET ZERO
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    
    labels = [
        'Uendret\nRun-Rate',
        'Vikarbyrå-\nstopp',
        'Turnus &\nOvertid',
        'Innkjøps-\nfrys',
        'NAV Refusj.\nAvstemming',
        'Ressurskr.\nTilskudd',
        'Målresultat\n31.12'
    ]
    # Starter på -3 344 kNOK (merforbruk), henter inn tiltak
    bottoms = [-3344, -3344, -2344, -1224, -1024, -374, 0]
    heights = [-3344, 1000, 1120, 200, 650, 374, 0]
    
    # Tilpass stolper
    bar_bottoms = [0, -3344, -2344, -1224, -1024, -374, 0]
    bar_heights = [-3344, 1000, 1120, 200, 650, 374, 0]
    bar_colors = ['#DC2626', '#22C55E', '#16A34A', '#22C55E', '#15803D', '#16A34A', '#0F172A']
    
    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, bar_heights, bottom=bar_bottoms, color=bar_colors, width=0.55)
    
    ax.axhline(0, color='#0F172A', linewidth=1.2)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=8.5, fontweight='medium')
    ax.set_ylabel('Akkumulert Avvik (tusen kr)', fontsize=9, color='#475569')
    ax.set_title('Konsolidert Vannfall: Lukking av Merforbruket mot Net Zero Budsjettbalanse (tusen kr)', fontsize=11, fontweight='bold', color='#0F172A', pad=12)
    
    # Tekst på stolper
    for idx, (h, b) in enumerate(zip(bar_heights, bar_bottoms)):
        if idx == 0:
            txt = "-3 344 k\n(Sprekk)"
            pos_y = -1672
        elif idx == len(labels) - 1:
            txt = "0 kr\n(Net Zero)"
            pos_y = 150
        else:
            txt = f"+{h} k"
            pos_y = b + h / 2
        ax.text(idx, pos_y, txt, ha='center', va='center', fontsize=8, fontweight='bold',
                color='#FFFFFF' if idx in [0, 1, 2, 4] else '#0F172A')

    ax.set_ylim(-3800, 700)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    chart3_path = REPORTS_DIR / "chart_netzero_waterfall.png"
    plt.savefig(chart3_path)
    plt.close()
    print(f"[OK] Graf 3 lagret: {chart3_path}")


if __name__ == "__main__":
    generate_charts()
