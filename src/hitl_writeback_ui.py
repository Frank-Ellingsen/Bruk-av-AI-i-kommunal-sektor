#!/usr/bin/env python3
"""
============================================================================
KRISTIANSAND KOMMUNE - HUMAN-IN-THE-LOOP (HITL) WRITE-BACK UI
Purpose: Glass-box AI audit, review, and human sign-off application.
Stack: Streamlit + SQLite Golden Record (kristiansand_golden_record.db)
============================================================================
"""

import datetime
import sqlite3

import pandas as pd
import streamlit as st

try:
    from config import DB_PATH
except ModuleNotFoundError:  # pragma: no cover - package import fallback
    from src.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_audit_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Audit_AI_Actions (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tidsstempel TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        enhet_kode TEXT NOT NULL,
        ai_modell_versjon TEXT NOT NULL,
        prognostisert_avvik REAL NOT NULL,
        foreslatt_tiltak TEXT NOT NULL,
        konfidens_score REAL NOT NULL,
        leder_beslutning TEXT CHECK (leder_beslutning IN ('GODKJENT', 'AVVIST', 'ENDRET', 'APPROVED', 'REJECTED', 'MODIFIED')),
        begrunnelse_tekst TEXT,
        godkjent_av_saksbehandler TEXT NOT NULL,
        IP_adresse TEXT
    );
    """)
    conn.commit()
    conn.close()

def main():
    # Initialize Page Config
    st.set_page_config(
        page_title="Kristiansand Kommune - HITL AI Governance Portal",
        page_icon="🏛️",
        layout="wide"
    )

    init_audit_table()

    st.title("🏛️ Kristiansand Kommune — AI Glass-Box & HITL Sign-off Portal")
    st.markdown("**Styremodell:** Stage-Gate 3 (Human-in-the-Loop) | EU AI Act Art. 14 Oversight | GDPR Art. 35 DPIA")

    st.divider()

    # Sidebar: User Authentication Context
    st.sidebar.header("👤 Saksbehandler Identitet")
    user_name = st.sidebar.text_input("Saksbehandler / Rådgiver", "Frank Ellingsen")
    st.sidebar.selectbox("Rolle / Fullmakt", ["Rådgiver Økonomi", "Enhetsleder Skole", "Enhetsleder Boenhet", "Kommunalsjef"])
    st.sidebar.selectbox("Sektor", ["Oppvekst", "Helse og mestring", "By- og stedsutvikling"])

    # Section 1: Active Variance Case Review
    st.subheader("1. Velg Registrert Avvikssak for AI-Diagnose")

    cases = {
        "CASE-2026-001": {
            "Enhet": "Kommunal Skole",
            "Sektor": "Oppvekst",
            "KOSTRA_Art": "1020 Sykemeldte vikarer",
            "YTD_Avvik": 47000.0,
            "Budsjett_YTD": 30000.0,
            "Regnskap_YTD": 77000.0,
            "Related_Art_1690": -25000.0,
            "AI_Reasoning": [
                "1. Art 1020 (Sykemeldte vikarer) viser et akkumulert merforbruk på +kr 47 000 per T1.",
                "2. Koblet analyse mot Art 1690 (NAV-refusjon) avdekker uinntektsført refusjon på kr 25 000 som følge av forsinkelser i Visma ERP-omleggingen.",
                "3. Underliggende reell merbelastning på vikarbruk er reduktivt kr 22 000 (innenfor 5 % akseptabel driftsmargin).",
                "4. Ingen faste stillingshjemler er overskredet."
            ],
            "AI_Action": "Opprett formell purring mot NAV for ubetalt refusjon (art 1690). Omdisponer kr 22 000 fra ubenyttet lønnsreserve på art 1010.",
            "Governance_Ref": "Kommuneloven § 14-6 (Bruttoprinsippet) & KOSTRA Veileder Art 1690",
            "Confidence": 0.94
        },
        "CASE-2026-002": {
            "Enhet": "Kommunal Boenhet",
            "Sektor": "Helse og mestring",
            "KOSTRA_Art": "1090 Overtid helgetillegg",
            "YTD_Avvik": 117000.0,
            "Budsjett_YTD": 60000.0,
            "Regnskap_YTD": 177000.0,
            "Related_Art_1690": -40000.0,
            "AI_Reasoning": [
                "1. Art 1090 (Overtid) viser kritisk avvik på +kr 117 000 (+195 % mot periodisert budget).",
                "2. Turnusanalysen indikerer 24/7-dekning ved vakanser og sammensatte brukerbehov i helgeadministrasjon.",
                "3. Høy vikarinnleie fra eksterne byråer har forsterket avviket.",
                "4. NAV-refusjon etterslep er estimert til kr 40 000."
            ],
            "AI_Action": "Aktiver kommunal intern vikarpool for helgedekning T2. Fremme sak for kommunalsjef om rammeregulering dersom brukerpågang vedvarer.",
            "Governance_Ref": "Arbeidsmiljøloven § 10-6 & Delegeringsreglementet Kristiansand Kommune",
            "Confidence": 0.89
        }
    }

    selected_case_id = st.selectbox("Velg sak fra oversikten:", list(cases.keys()))
    case_data = cases[selected_case_id]

    # Display Case Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Enhet", case_data["Enhet"])
    col2.metric("KOSTRA Art", case_data["KOSTRA_Art"])
    col3.metric("YTD Avvik", f"kr {case_data['YTD_Avvik']:,.0f}")
    col4.metric("NAV Etterslep (Art 1690)", f"kr {case_data['Related_Art_1690']:,.0f}")

    st.divider()

    # Section 2: Transparent AI Glass-Box Explanation
    st.subheader("2. 🔍 AI Glass-Box Årsaksforklaring & RAG-Begrunnelse")

    with st.expander("Se AI-modellens stegvis resonneringsrekke (Ingen Black Box)", expanded=True):
        st.write("**Forklaringskjede (Chain of Thought):**")
        for step in case_data["AI_Reasoning"]:
            st.write(f"- {step}")
        
        st.info(f"📜 **Regelverksforankring (RAG):** {case_data['Governance_Ref']}")
        st.caption(f"🤖 **Modellens konfidensscore:** {case_data['Confidence']*100:.1f} %")

    st.divider()

    # Section 3: Human Sign-off and Action Execution Form
    st.subheader("3. ✍️ Saksbehandlers Beslutning & Sign-off (HITL)")

    with st.form("hitl_signoff_form"):
        st.write(f"**Anbefalt administrative tiltak:** {case_data['AI_Action']}")
        
        user_action = st.radio(
            "Velg din beslutning som saksbehandler:",
            ["APPROVED", "MODIFIED", "REJECTED"],
            format_func=lambda x: {
                "APPROVED": "✅ Godkjenn tiltak (Full overensstemmelse)",
                "MODIFIED": "✏️ Godkjenn med modifikasjoner",
                "REJECTED": "❌ Avvis tiltak (Krever begrunnelse)"
            }[x]
        )
        
        user_notes = st.text_area(
            "Saksbehandlers begrunnelse / Notat til revisjonssporet:",
            placeholder="Skriv inn kommentar om lokal kontekst, vurdering eller endring i tiltaket..."
        )
        
        submitted = st.form_submit_button("🔒 Bekreft og Før i Audit Trail")

    if submitted:
        beslutning_map = {
            "APPROVED": "GODKJENT",
            "MODIFIED": "ENDRET",
            "REJECTED": "AVVIST"
        }
        leder_beslutning = beslutning_map.get(user_action, "GODKJENT")
        enhet_kode = "2020" if "Skole" in case_data["Enhet"] else "2540"
        
        # Bygg fyldig revisjonsnotat med RAG-referanse og saksbehandlers kommentar
        begrunnelse_tekst = f"{user_notes.strip()} | Lovhjemmel: {case_data['Governance_Ref']} | AI-begrunnelse: {' '.join(case_data['AI_Reasoning'][:2])}"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Audit_AI_Actions (
                tidsstempel, enhet_kode, ai_modell_versjon, prognostisert_avvik,
                foreslatt_tiltak, konfidens_score, leder_beslutning, begrunnelse_tekst,
                godkjent_av_saksbehandler, IP_adresse
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            enhet_kode,
            "Antigravity-EPM-v2.4 / Glass-Box RAG",
            case_data["YTD_Avvik"],
            case_data["AI_Action"],
            case_data["Confidence"],
            leder_beslutning,
            begrunnelse_tekst,
            user_name,
            "10.140.22.15"
        ))
        conn.commit()
        conn.close()
        st.success(f"Saken er behandlet og signert av {user_name}! Beslutning `{leder_beslutning}` er registrert i `Audit_AI_Actions`.")

    st.divider()

    # Section 4: Display Audit Log
    st.subheader("4. 📋 Offisiell Audit Trail Logg (SQLite Golden Record)")
    conn = get_db_connection()
    df_audit = pd.read_sql_query("""
        SELECT 
            log_id AS 'Logg ID',
            tidsstempel AS 'Tidspunkt',
            enhet_kode AS 'Enhetskode',
            foreslatt_tiltak AS 'AI-anbefaling',
            ROUND(konfidens_score * 100, 1) || ' %' AS 'Konfidens',
            leder_beslutning AS 'Beslutning',
            godkjent_av_saksbehandler AS 'Saksbehandler',
            begrunnelse_tekst AS 'Begrunnelse & Revisjonsnotat'
        FROM Audit_AI_Actions 
        ORDER BY tidsstempel DESC
    """, conn)
    conn.close()

    st.dataframe(df_audit, use_container_width=True)


if __name__ == "__main__":
    main()
