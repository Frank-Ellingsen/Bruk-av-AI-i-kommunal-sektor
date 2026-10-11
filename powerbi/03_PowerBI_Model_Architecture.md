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

### Side 2: Mevold Grunnskole (KOSTRA 202 – Rammestyrt Enhet)
* **Fokus:** Lønnsforbruk, vikartimer og etterslep på refusjoner.
* **Visual 1 (Avviksfordeling - Diverging Bar Chart):**
  * Akse: `Fact_Regnskap[Kontonavn]`
  * Verdi: `[Avvik YTD]`
  * Viser tydelig overforbruk på *Fast lønn lærere* og *Lønn til ekstrahjelp* mot mindreforbruk på drift.
* **Visual 2 (NAV Sykelønnsavstemming):**
  * Mål: `[NAV Refusjoner Bokført YTD]` mot historisk forventet refusjon.

### Side 3: Slettheia Bofellesskap (KOSTRA 254 – Døgnbemannet Enhet)
* **Fokus:** 24/7 Turnus, overtid, helgetillegg og eksterne vikarbyråer.
* **Visual 1 (Lønnsstruktur - Decomposition Tree):**
  * Rute: `[Avvik YTD]` (+1,29 mill. kr)
  * Forklares av:
    1. *Kjøp av vikarbyråtjenester (art 127040):* +383 000 kr
    2. *Fastlønn ordinære (art 101000):* +475 000 kr
    3. *Vikar natt/kveldstillegg (art 102031):* +259 000 kr
    4. *Overtidslønn (art 104000):* +186 000 kr
* **Visual 2 (Månedlig Lønnsutvikling - Linjediagram med direkte merking):**
  * X-akse: `Dim_Dato[ar_maned]` (Jan–Aug)
  * Linje 1: `Budsjett` (Stiplet grå)
  * Linje 2: `Regnskap` (Heltrukket mørkeblå)

### Side 4: Ansvarlig AI & Preskriptiv Tiltaksmeny (HITL Audit Trail)
* **Tabell (Audit Trail fra `Audit_AI_Actions`):**
  * Kolonner: `Tidsstempel`, `Enhetskode`, `AI Tiltak`, `Konfidens`, `Leder Beslutning`, `Saksbehandler`, `Begrunnelse`.
  * Demonstrerer etterlevelse av **Kommuneloven § 14-5** og **EU AI Act**.
