# Power BI Datamodell & Rapportarkitektur: Kristiansand EPM
## Implementasjonsveileder for BoMiljø (Slettheia) og Komskole (Mevold)

---

## 1. Relasjonsdiagram (Star Schema i Power BI Model View)

I Power BI Desktop settes følgende relasjoner opp med **Enkeltveis kryssfiltrering (Single)** og **1-til-mange (1:*)**:

```
        ┌───────────────────┐
        │   Dim_Funksjon    │
        │ ───────────────── │
        │ * funksjon_kode   │
        └─────────┬─────────┘
                  │ 1
                  │ *
┌─────────────────┴─┐       ┌───────────────────┐
│   Dim_Ansvar      │       │     Dim_Dato      │
│ ───────────────── │       │ ───────────────── │
│ * ansvar_kode     │       │ * dato_key        │
└─────────┬─────────┘       └─────────┬─────────┘
          │ 1                         │ 1
          │ *                         │ *
    ┌─────┴───────────────────────────┴─────┐
    │             Fact_Regnskap             │
    │ ───────────────────────────────────── │
    │ * transaksjon_id (PK)                 │
    │ * dato_key (FK)                       │
    │ * funksjon_kode (FK)                  │
    │ * ansvar_kode (FK)                    │
    │   KOSTRA_Art                          │
    │   Kontokode                           │
    │   Kontonavn                           │
    │   Budsjett (Valuta)                   │
    │   Regnskap (Valuta)                   │
    │   Avvik (Valuta)                      │
    │   Merforbruk (Valuta)                 │
    └───────────────────────────────────────┘
```

### Modellinnstillinger i Power BI:
1. **Skjul fremmednøkler:** Skjul `dato_key`, `funksjon_kode` og `ansvar_kode` i `Fact_Regnskap`. Bruk alltid dimensjonstabellene i visualiseringer og slicere.
2. **Sortering etter kolonne:** Merk `Dim_Dato[manedsnavn]` $\rightarrow$ Velg *Sorter etter kolonne (Sort by Column)* $\rightarrow$ Velg `Dim_Dato[maned]`.
3. **Måltabell:** Opprett en tom tabell `_Measures` og legg alle DAX-mål fra `02_DAX_Measures_Library.dax` her.

---

## 2. Row-Level Security (RLS) Roller

I henhold til delegeringsreglementet i Kristiansand kommune konfigureres RLS under *Modellering $\rightarrow$ Behandle roller*:

| Rolle | Tabell | DAX Filteruttrykk | Målgruppe |
| :--- | :--- | :--- | :--- |
| **Enhetsleder_Skole** | `Dim_Ansvar` | `[ansvar_kode] = "2020"` | Rektor Mevold Grunnskole |
| **Enhetsleder_Boenhet** | `Dim_Ansvar` | `[ansvar_kode] = "2540"` | Avdelingsleder Slettheia Bofellesskap |
| **Kommunalsjef_Oppvekst**| `Dim_Ansvar` | `[kommunalsjefomrade] = "Oppvekst"` | Kommunalsjef og stabscontrollere |
| **Kommunalsjef_Helse** | `Dim_Ansvar` | `[kommunalsjefomrade] = "Helse og mestring"` | Kommunalsjef Helse og mestring |
| **Konsern_Okonomi** | *Ingen* | *Full tilgang (ingen filter)* | Økonomidirektør & Sentral økonomistab |

---

## 3. Rapportdesign i henhold til Edward Tuftes Data-Ink Standarder

Rapporten bygges med 4 dedikerte sider med maksimalt data-ink ratio (ingen 3D, ingen skygger, ingen vertikale linjer):

### Side 1: Konsern- og Sektoroverblikk (T2 Status & EOY Prognose)
* **Toppkort (KPI Tiles - Hvite med dempet ramme, ingen skygger):**
  * `Regnskap YTD`: 26,7 mill. kr
  * `Budsjett YTD`: 24,5 mill. kr
  * `Avvik YTD`: **+2,28 mill. kr** (Fremhevet med `#C53030`)
  * `EOY Forventet Årsavvik`: **+3,42 mill. kr**
* **Hovedmatrise (KOSTRA Sektornivå):**
  * Rader: `Dim_Ansvar[kommunalsjefomrade]` $\rightarrow$ `Dim_Ansvar[ansvar_navn]`
  * Kolonner: `Budsjett YTD`, `Regnskap YTD`, `Avvik YTD`, `Avvik YTD %`, `EOY Prognose`
  * Betinget formatering: Bakgrunn styres av målet `[Tufte_Avvik_Farge_HEX]`.

### Side 2: Mevold Grunnskole (KOSTRA 202 – Framsikt Visual Layout)
*Inspirert av skole1.png, skole2.png og skole_framsikt_cond_format.png:*
* **Hovedtabell / Matrise (Betinget formatering med Data Bars og KPI-flagg):**
  * Rader: `Enhet (brukt)` (Ordinær undervisning, Spesialundervisning, Grunnskole, SFO, Voksenopplæring, Skoleskyss, PPT, Leirskole).
  * Kolonner: 
    * `Regnskap hiå` (med grå in-cell Data Bars)
    * `Budsjett hiå`
    * `Avvik i kr` (med 🚩 rødt flagg for negative avvik: -639 kNOK, -296 kNOK, -170 kNOK)
    * `Avvik i prosent` (-6 %, -12 %, -21 %)
    * `Årsbudsjett` (17 590 kNOK, 4 114 kNOK, osv. | Total 27 490 kNOK)
    * `Brukt hiå` (med progress indikator / signalikoner)
* **Kontotype Avvik (Diverging Bar / Tornado Chart):**
  * Lønn: -1 302 kNOK
  * Overføringsutgifter: -262 kNOK
  * Finansutgifter: -250 kNOK
  * Overføringsinntekter: +176 kNOK
  * Salg av varer/tjenester: +611 kNOK
* **Topp 5 Negative og Positive Kontoer:**
  * Topp Negativ: Fastlønn lærere (-1 436 kNOK), Lønn til vikarer (-381 kNOK), Sykevikarer (-272 kNOK), Overtid (-230 kNOK).
  * Topp Positiv: Refusjon fødselspenger (+979 kNOK), Sykelønnsrefusjon (+449 kNOK), Momskompensasjon (+266 kNOK).

### Side 3: Slettheia Bofellesskap (KOSTRA 254 – Framsikt Visual Layout)
*Inspirert av boom1.png og boom2.png:*
* **Gauge & Månedskort:**
  * Halvsirkel-gauge: Regnskap YTD 12 630 912 kr vs Budsjett YTD 11 337 125 kr (Avvik -1 293 787 kr / -11 %).
  * Siste måned i valgt periode (August): Regnskap 1 765 810 kr vs Budsjett 1 525 148 kr (Avvik -240 662 kr / -16 %).
* **Dekomponering (Decomposition Tree / Vannfall):**
  * Samlet avvik (-1 293 787 kr) splittet i:
    * `1 Lønn`: -1 149 674 kr (-10 %)
    * `2 Utgifter (Drift)`: -144 113 kr
* **Månedlig Avvikstrend & Outliers (Jan–Aug):**
  * Tydelig fremheving av anomalier: Januar (+374 kNOK), Februar-sjokket (-675 kNOK merforbruk), Juni (-257 kNOK), Juli (-218 kNOK), August (-106 kNOK).
  * Fan chart / konfidensintervall for rullende fremskriving ut året.
* **Topp Drivere (Tornado):**
  * Kjøp av eksternt vikarbyrå (-383 kNOK), Vikar kveld/natt (-259 kNOK), Vikar helg (-141 kNOK), Overtid (-186 kNOK), Ekstrahjelp (-142 kNOK), Fastlønn (-475 kNOK).
  * Motvirket av tilskudd lærlinger (+160 kNOK) og foreldrepermisjonsrefusjoner (+190 kNOK).
* **Diagnostisk Innsiktsboks ("Lønn - funn"):**
  * Strukturert analyse av turnusskjevhet, helgebruk og ferieavvikling.

### Side 4: Net Zero Balanseringsplan & Tiltakseffekt (Mål: 0 kr i EOY-avvik)
* **Status vs Tiltaksbane:**
  * Viser uendret run-rate prognose (Slettheia: -1,93 MNOK / Mevold: -1,42 MNOK) mot iverksatte tiltak.
  * Månedlig tiltaksprofil (September - Desember) som faser inn kostnadskutt og refusjonsinnkreving.
  * Sluttavvik per 31.12 = **0 kr** (100 % balanse mot årsbudsjett).
* **Tiltaksmatrise:**
  * Tabell med ansvarlig enhetsleder, tiltakskategori, månedlig effektprofil og juridisk forankring.

### Side 5: Ansvarlig AI & Human-in-the-Loop Audit Trail
* **Tabell (Audit Trail fra `Audit_AI_Actions`):**
  * Kolonner: `Tidsstempel`, `Enhetskode`, `AI Tiltak`, `Konfidens`, `Leder Beslutning`, `Saksbehandler`, `Begrunnelse`.
  * Demonstrerer etterlevelse av **Kommuneloven § 14-5** og **EU AI Act**.

---

## 4. KOSTRA Lovpålagte Nøkkeltall & Handlingsregler

For offisiell rapportering og bystyrenivå integrerer modellen lovpålagte KOSTRA-nøkkeltall (jf. [docs/dax_kostra_kpi_package.md](file:///c:/Users/frank/Desktop/KrsKom/use%20cases/docs/dax_kostra_kpi_package.md) og [powerbi/04_KOSTRA_DAX_KPI_Package.dax](file:///c:/Users/frank/Desktop/KrsKom/use%20cases/powerbi/04_KOSTRA_DAX_KPI_Package.dax)):

* **Brutto Driftsresultat %:** Minimum 1,7 % over tid (Handlingsregel Kristiansand kommune).
* **Korrigert Netto Driftsresultat %:** Minimum 1,0 % jf. 1. tertialrapport 2026.
* **Disposisjonsfond Grad %:** Minimum 5,0 % bufferkapital av brutto driftsinntekter.
* **Gjeldstak / Nettogjeld:** Maksimalt 8,8 mrd. kr (Bystyrevedtak HØP 2026–2029).
* **Vesentlighetsterskel:** > 5,0 % eller 500' kr utløser krav om tiltak og rapportering jf. Økonomireglementet § 4.


