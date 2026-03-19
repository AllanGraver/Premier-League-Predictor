# Premier League – Predictions (UI Scenario 1)

Denne version viser **Sejrschancer + Trafiklys + Top‑scorelines** (uden rå ratingtal):
- **Chancer** (H/U/B) i procenter
- **Kampbillede** (trafiklys‑label: Klar favorit / Åben kamp) + ⚠️ upset‑ikon
- **Top‑3 scorelines** pr. kamp
- **Forventede mål (λ)** for hjemme/ude

## Opsætning (5 min)
1) Opret football-data.org token og gem som GitHub secret `FOOTBALL_DATA_TOKEN`  
2) Commit alle filer til et nyt repo og kør workflow under **Actions**  

## Konfiguration
Se `config.yml` – med **forklarende kommentarer** til hver indstilling (model + UI).

## Output
- `data/matches.csv` – kommende kampe
- `data/xgelo_ratings.csv` – interne ratings (bruges i beregning, skjules i UI)
- `data/predictions.csv` – sandsynligheder + top‑scorelines
- `reports/predictions.md` – publikumsegnet rapport (Scenario 1)

> Bemærk: Data hentes fra football-data.org (fixtures) og FBref (match xG).
