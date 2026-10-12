# Kristiansand Kommune — Agentisk EPM & AI Rammeverk (Norsk Versjon)

Dette rammeverket utgjør en komplett, ansvarlig og RAG-forankret Enterprise Performance Management (EPM) arkitektur for Kristiansand kommune.

## 📁 Mappestruktur (Norsk)

```text
kristiansand_epm_rammeverk_norsk/
├── README_NO.md                              <- Denne hovedveilederen
├── agent_ferdigheter/                        <- Spesialiserte agent-instruksjoner (.md)
│   ├── 01_dataintegrasjon_etl_agent.md
│   ├── 02_bi_dax_modellering_agent.md
│   ├── 03_prediktiv_anomali_agent.md
│   ├── 04_preskriptiv_hitl_agent.md
│   ├── 05_etikk_styring_portvakt_agent.md
│   ├── 06_ledelsesrapport_skribent_agent.md
│   ├── 07_excel_powerbi_rapportering_agent.md
│   └── 08_flerniva_interessent_rapportering_agent.md
├── dokumentasjon/                            <- Fullstendig systemdokumentasjon
│   ├── epm_fullstendig_arbeidsflyt.md
│   ├── antigravity_brukstilfelle_epm.md
│   ├── dax_kostra_kpi_pakke.md
│   └── rag_kunnskapsbase_spesifikasjon.md
├── rag_kunnskapsbase/                        <- DEDIKERT MAPPE FOR RAG-KILDER OG REGLER
│   ├── kostra_veiledere/                     <- KOSTRA kontoplanveiledere (SSB / Regjeringen)
│   ├── kommunale_reglementer/               <- Økonomireglement, Delegeringsreglement, Tertialrapporter
│   └── lovverk_og_etikk/                     <- Kommuneloven, GDPR, EU AI Act Art. 27 (FRIA)
├── data/                                     <- Datagrunnlag
│   ├── kostra_kontoplan.csv                  <- Komplett KOSTRA-kontoplan
│   └── kristiansand_golden_record.db         <- SQLite Golden Record database
├── kildekode/                                <- Produksjonsklar kildekode
│   ├── datalinje/epm_agent_pipeline.py       <- Python ETL, Golden Record & Audit Log
│   ├── powerbi/fxOpenAI_RAG.m                <- Power Query M-funksjon for manuell RAG-utløsning
│   └── brukergrensesnitt/hitl_skriveback_ui.py<- Streamlit Glass-Box Controller UI
└── ressurser/                                <- Diagrammer og grafikk
    └── epm_arbeidsflyt_diagram.png           <- Arkitekturdiagram
```

## 🛡️ Sikkerhet, Personvern & RAG-arkitektur

- **Manuell utløsning (Human-in-the-Loop):** Ingen uønskede automatiserte køer eller API-kall.
- **Enterprise AI Provider:** Bruk av Azure OpenAI (Norge/EU-region) med Databehandleravtale (DPA) og Zero Data Retention (ZDR).
- **Lokal LLM-klargjøring:** Arkitekturen er 100 % kompatibel med å bytte til lokal LLM (f.eks. Ollama / Llama 3 70B / Mistral) ved fremtidig maskinvareoppgradering.
- **RAG-Forankring:** AI-modellen henter eksplisitte kontekstregler fra `rag_kunnskapsbase/` før det gis preskriptive tiltaksanbefalinger.
