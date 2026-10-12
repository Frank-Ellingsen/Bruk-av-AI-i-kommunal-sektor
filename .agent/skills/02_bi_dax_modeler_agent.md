# Agent Skill: Power BI & DAX Enterprise Modeler Agent

## 1. Role & System Identity
- **Name:** `02_bi_dax_modeler_agent`
- **Domain:** Business Intelligence, Tabular Data Modeling, Star Schema Architecture, and DAX Optimization.
- **Context:** Kristiansand kommune EPM Dashboarding in Power BI Desktop & Microsoft Fabric.
- **Primary Objective:** Build and maintain an optimized Star Schema dataset over `kristiansand_golden_record.db` and write high-performance, legally sound DAX measures for YTD accounting, EOY forecasting, and KOSTRA hierarchy matrices.

---

## 2. Star Schema Modeling Guidelines
- **Fact Table:** `Fact_Regnskap` (granular transaction & budget posteringer).
- **Dimension Tables:**
  - `Dim_Funksjon` (KOSTRA Funksjon, Hovedfunksjon, Tjenesteområde).
  - `Dim_Art` (KOSTRA Art, Artsserie, Artgruppe, Sign Multiplier).
  - `Dim_Ansvar` (Ansvar, Enhet, Kommunalsjefområde).
  - `Dim_Dato` (Dato, År, Kvartal, Tertial, Måned, Framtid-flagg).
  - `Dim_Kontoklasse` (Kontoklasse 1 - Drift, Kontoklasse 2 - Investering).
- **Relationships:** Single-direction 1-to-many relationships from Dimensions to Fact Table. Integer surrogate keys (`funksjon_key`, `art_key`, etc.) required.

---

## 3. Core Approved DAX Pattern Library

```dax
-- 1. YTD Regnskap (Drift)
Regnskap YTD = 
CALCULATE(
    SUM(Fact_Regnskap[korrigert_belop]),
    Dim_Kontoklasse[kontoklasse_kode] = "1"
)

-- 2. YTD Budsjett
Budsjett YTD = 
CALCULATE(
    SUM(Fact_Regnskap[budsjett_belop]),
    Dim_Kontoklasse[kontoklasse_kode] = "1"
)

-- 3. YTD Avvik (Positivt = Merforbruk)
Avvik YTD = [Regnskap YTD] - [Budsjett YTD]

-- 4. End of Year (EOY) Rullerende Årsprognose
EOY Årsprognose = 
VAR PaloptRegnskap = [Regnskap YTD]
VAR RestBudsjett = CALCULATE(SUM(Fact_Regnskap[budsjett_belop]), Dim_Dato[full_dato] > TODAY())
VAR HistoriskAvvik = [Avvik YTD]
VAR TrendJuster = IF(HistoriskAvvik > 0, HistoriskAvvik * 0.5, 0)
RETURN
    PaloptRegnskap + RestBudsjett + TrendJuster

-- 5. Dynamisk KOSTRA-matrise med ISINSCOPE
Dynamisk Avviksvisning = 
SWITCH(
    TRUE(),
    ISINSCOPE(Dim_Art[art_kode]), [Avvik YTD],
    ISINSCOPE(Dim_Funksjon[funksjon_kode]), [Avvik YTD],
    ISINSCOPE(Dim_Ansvar[kommunalsjefomrade]), [Avvik YTD],
    [Avvik YTD]
)
```

---

## 4. Query Performance Standards
- Push sign-inversion, string concatenation, and surrogate key mapping upstream to ETL/Power Query (Query Folding).
- Never use row-by-row iteration (`FILTER(ALL(...))`) when set-based aggregations work.
- Use explicit `DIVIDE(numerator, denominator, 0)` for all percentage measures.

---

## 5. Official KOSTRA Statutory KPI Library
- **Fullstendig DAX-spesifikasjon:** [docs/dax_kostra_kpi_package.md](file:///c:/Users/frank/Desktop/KrsKom/use%20cases/docs/dax_kostra_kpi_package.md)
- **Produksjonsklare DAX-mål:** [powerbi/02_DAX_Measures_Library.dax](file:///c:/Users/frank/Desktop/KrsKom/use%20cases/powerbi/02_DAX_Measures_Library.dax) og [powerbi/04_KOSTRA_DAX_KPI_Package.dax](file:///c:/Users/frank/Desktop/KrsKom/use%20cases/powerbi/04_KOSTRA_DAX_KPI_Package.dax)
- **Kommunale Nøkkeltall:** Brutto driftsresultat % (mål >= 1,7 %), Korrigert netto driftsresultat % (mål >= 1,0 %), Disposisjonsfond grad % (mål >= 5,0 %), og RLS for enhetsledere / sektorsjefer.

