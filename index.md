# 🏛️ Kristiansand Kommune — Control Office Hub ("The Office")
> **Operativ Styringshub og Navigasjonssenter for Rådgiver Økonomistyring & Økonomidirektør (Supervisor)**

---

## 👥 1. Rollearkitektur & Supervisor-Matrise

| Rolle | Hovedansvar i Styringssløyfen | Systemflate & Verktøy | Godkjenningsmyndighet |
| :--- | :--- | :--- | :--- |
| **Økonomidirektør** *(Supervisor)* | Overordnet strategisk resultatansvar, politisk innstilling av tertialrapporter og HØP, Stage-Gate godkjenning. | Executive Power BI, PDF Briefing, Word Saksfremlegg | Endelig kommunal innstilling til Bystyret |
| **Rådgiver Økonomistyring** *(HITL Controller)* | Daglig avvikskontroll, nøytralisering av Visma ERP-etterslep (art 1690), What-If scenariomodellering, RAG-evaluering og HITL-sign-off. | Power BI, Excel What-If, Controller AI Portal, Teams | HITL-overprøving (`APPROVED` / `MODIFIED` / `REJECTED`) |
| **Kommunalsjef** *(Sektorleder)* | Sektorvis rammestyring, godkjenning av omdisponeringer innenfor sektoren jf. Økonomireglementet § 4.2. | Power BI Sektormatrise, Framsikt | Rammeomdisponering internt i sektor |
| **Enhetsleder** *(Grunnskole / Boenhet)* | Lokal enhetsstyring, oppfølging av fraværstiltak og vikarforbruk. | Teams Adaptive Cards, Framsikt | Operative driftstiltak |
| **DPO & IT-Sikkerhetsansvarlig** | Overvåking av personvern (DPIA), etikk (FRIA), PII-skjerming og uforanderlig SHA-256 Audit Log. | `pii_scrubber.py`, Algoritmeregister, Audit Log | Sikkerhets- og etikk-godkjenning (Gates 1–10) |

---

## 🗓️ 2. Det Kommunale Årshjulet 2026 (Tidsfrister & Status)

### 🔵 Kvartal 1: Årsavslutning & KOSTRA-Rapportering
- [x] **15. januar:** Innsending av KOSTRA helse- og omsorgsskjemaer (Skjema 4, 5, 11, 15) til SSB.
- [x] **23. februar:** Obligatorisk innsending av regnskapsfiler (Skjema 0A, 0B, 0M, 0N) til SSB.
- [x] **09. mars:** Endelig regnskapsavslutning og avstemming av årsregnskap 2025.
- [x] **15. mars:** SSB publiserer ureviderte KOSTRA-tall *(Auto-oppdatering av RAG-kunnskapsbasen)*.
- [x] **31. mars:** Kommunedirektørens ferdigstilling av Årsrapport og Årsregnskap 2025.

### 🟢 Kvartal 2: 1. Tertialrapport (T1) & Revidert Nasjonalbudsjett (RNB)
- [x] **15. april:** Kommunal Revisjon avgir revisjonsberetning for 2025.
- [x] **20. mai:** Bystyrets behandling og godkjenning av Årsregnskap 2025.
- [/] **25. mai:** Fremleggelse av **1. tertialrapport 2026 (T1)** *(Med Visma ERP-korreksjon og EOY-prognose)*.
- [ ] **02. juni:** Regjeringen fremlegger Revidert nasjonalbudsjett (RNB).
- [ ] **15. juni:** SSB publiserer endelige KOSTRA-tall *(ASSS-benchmarks oppdateres)*.

### 🟡 Kvartal 3: 2. Tertialrapport (T2) & HØP 2027–2030 Forberedelser
- [ ] **15. august:** Innspill fra tjenesteområdene til ny Handlings- og økonomiplan (HØP).
- [ ] **23. september:** Kommunedirektørens forslag til HØP 2027–2030 fremlegges.
- [ ] **28. september:** Behandling og vedtak av **2. tertialrapport (T2)** i Formannskapet og Bystyret.

### 🔴 Kvartal 4: Statsbudsjett & Bystyrets Endelige Budsjettvedtak
- [ ] **07. oktober:** Regjeringen fremlegger Statsbudsjettet 2027.
- [ ] **25. november:** Formannskapets innstilling til HØP og Årsbudsjett offentliggjøres for høring.
- [ ] **18. desember:** **Bystyrets endelige vedtak** av Årsbudsjett 2027 og HØP 2027–2030 (Kommuneloven § 14-3).

---

## 📂 3. Prosjektarkiv & Underliggende Dokumentasjon

### 📄 Ledelses- og Saksdokumenter
- **[Saksfremlegg Word (`saksfremlegg_epm_okonomidirektor.docx`)](./saksfremlegg_epm_okonomidirektor.docx):** Formelt saksfremlegg med 4 vedtakspunkter for Bystyret/Lederteamet.
- **[Executive PowerPoint (`epm_presentasjon_okonomidirektor.pptx`)](./epm_presentasjon_okonomidirektor.pptx):** 8-slide stram presentasjon skreddersydd for Økonomidirektøren.
- **[PDF Executive Briefing (`epm_sammendrag_kristiansand.pdf`)](./epm_sammendrag_kristiansand.pdf):** 1-sides visuelt ledelsessammendrag for styringsmøter.
- **[Anbud Kravspesifikasjon (`kravspesifikasjon_ai_innkjop.docx`)](./kravspesifikasjon_ai_innkjop.docx):** Bilag 1 Kravspesifikasjon for AI-innkjøp jf. GDPR, EU AI Act, NIS2 og CRA.
- **[Anbud Evalueringsskjema (`tildelingsskjema_ai_anbud.xlsx`)](./tildelingsskjema_ai_anbud.xlsx):** Interaktivt Excel-skjema for poengsetting og veid evaluering (0–10 skala).

### 📊 Modeller & Dashboards
- **[Excel EPM What-If Modell (`kristiansand_epm_modell.xlsx`)](./kristiansand_epm_modell.xlsx):** Dynamic What-If scenariomodell for Visma-etterslep og EOY-balanse.
- **[Control Office Hub Excel (`kontor_oversikt_og_arshjul.xlsx`)](./kontor_oversikt_og_arshjul.xlsx):** Interaktivt Excel Dashboard for Supervisor, Årshjul og operativ avsjekk.
- **[Arbeidsflytdiagram PNG (`kontor_arbeidsflyt_diagram.png`)](./kontor_arbeidsflyt_diagram.png):** Isometrisk oversiktsdiagram av den digitale styringssløyfen på kontoret.

### 💻 Kildekode & AI-Verktøy
- **`hitl_writeback_ui.py`:** Controller AI Portal UI (Streamlit) for RAG Glass-Box og SHA-256 Audit Log.
- **`pii_scrubber.py`:** Lokal anonymiseringsmodul for skjerming av FNR, navn og kontonumre før AI-oppslag.
- **`epm_agent_pipeline.py`:** ETL- og agent-pipeline for dataintegrasjon mot Visma, KOSTRA og Power BI.

---

## 📝 4. Operativ Sjekkliste for Økonomirådgiveren (HITL Workflow)

- [x] **Steg 1: Månedlig Visma-Eksport:** Hent ubehandlede saldoer for vikarbruk (art 1020) og NAV-refusjon (art 1690).
- [x] **Steg 2: PII-Skjerming:** Kjøre `pii_scrubber.py` for å garantere at ingen personopplysninger forlater kommunens infrastruktur.
- [x] **Steg 3: Power BI Avviksoppdaging:** Identifisér enheter med reelt underliggende merforbruk (`[Avvik YTD Korrigert] > 5%`).
- [x] **Steg 4: What-If Simulering:** Test fraværstiltak og rammejusteringer i Excel-modellen for å se EOY-balanseeffekten.
- [x] **Steg 5: RAG-Diagnose:** Kjøre AI-analyse i Controller-portalen for å hente kildeforankret hjemmel i Økonomireglementet og 1. tertialrapport.
- [x] **Steg 6: HITL Sign-Off:** Velg `APPROVED`, `MODIFIED` eller `REJECTED`, skriv saksbehandlernotat og lagre uforanderlig SHA-256 hash til `Audit_AI_Actions`.
- [x] **Steg 7: Teams-Varsling:** Send automatisk Adaptive Card til Teams-kanalen *Virksomhetsstyring* for avviksoppfølging.
- [x] **Steg 8: Iverksetting:** Registrér omdisponeringen i Framsikt/Visma og arkivér saksnotatet i Public360.

---

## 🛡️ 5. Stage-Gate Governance & Etikk-rammeverk

```text
[ Port 1: Behov ] ──> [ Port 2: DPIA/FRIA ] ──> [ Port 3: PII-Vask ] ──> [ Port 4: RAG Glass-Box ]
                                                                                   │
                                                                                   ▼
[ Port 8: Arkiv ] <── [ Port 7: Audit Log ] <── [ Port 6: HITL Sign-Off ] <── [ Port 5: What-If ]
```

1. **Human-in-the-Loop (HITL):** AI fatter **0 autonome beslutninger**.
2. **DPIA (GDPR Art. 35):** Klientbasert PII-skjerming garanterer at ingen personopplysninger benyttes i modelltrening eller eksterne API-er.
3. **FRIA (EU AI Act Art. 27):** Konsekvensvurderinger for å forhindre usaklig forskjellsbehandling mellom virksomhetsenheter.
4. **Audit Trail (EU AI Act Art. 12/26):** Uforanderlig lagring av alle behandlinger med SHA-256 transaksjons-hash.
5. **Algoritmeregister:** Offentlig registrering jf. Eurocities-standarden for full innbyggerinnsikt.
