# DAX KOSTRA KPI Package


---

## 6. ERP Visma-omlegging & Korreksjon for Periodiseringsstøy (Visma ERP Neutralization)

Når nytt ERP-system (Visma Enterprise) fører til forsinket bokføring av sykelønnsrefusjoner (art 1690), nøytraliserer disse DAX-måltallene periodiseringsstøyen slik at reelt underliggende driftsavvik avdekkes.

```dax
// 1. Bokført NAV-refusjon YTD (Art 1690)
[Bokført NAV Refusjon YTD] = 
CALCULATE(
    [Regnskap YTD],
    Dim_KOSTRA_Kontoplan[Niva_3_Kode] = "1690"
)

// 2. Forventet NAV-refusjon basert på vikarutgifter (Art 1020)
// Beregnet refunderbar andel satt til 65 % av påløpt sykevikarbruk
[Forventet NAV Refusjon YTD] = 
CALCULATE(
    [Regnskap YTD],
    Dim_KOSTRA_Kontoplan[Niva_3_Kode] = "1020"
) * -0.65

// 3. Beregnet ERP-etterslep (Bokføringsavvik på Art 1690)
[ERP NAV Refusjon Etterslep] = 
VAR _Etterslep = [Forventet NAV Refusjon YTD] - [Bokført NAV Refusjon YTD]
RETURN
    IF(_Etterslep < 0, _Etterslep, 0)

// 4. Korrigert Regnskap YTD (Nøytralisert for Visma-støy)
[Regnskap YTD Korrigert] = 
[Regnskap YTD] - [ERP NAV Refusjon Etterslep]

// 5. Reelt Underliggende Driftsavvik YTD
[Avvik YTD Korrigert] = 
[Regnskap YTD Korrigert] - [Budsjett YTD]
```
