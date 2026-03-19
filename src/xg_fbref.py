from __future__ import annotations

import io
import re
import requests
import pandas as pd

FBREF_PL_SCHEDULE_URL = "https://fbref.com/en/comps/9/schedule/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; xGEloBot/1.2; +https://github.com/)"}


def _read_html_table(content: bytes) -> pd.DataFrame:
    tables = pd.read_html(io.BytesIO(content))
    if not tables:
        raise RuntimeError("Could not find schedule table on FBref page")
    return max(tables, key=lambda d: d.shape[0])


def fetch_pl_schedule_with_xg() -> pd.DataFrame:
    r = requests.get(FBREF_PL_SCHEDULE_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    df = _read_html_table(r.content)

    cols = {str(c).lower(): c for c in df.columns}

    def pick(name: str):
        for k, v in cols.items():
            if k == name.lower():
                return v
        for k, v in cols.items():
            if name.lower() in k:
                return v
        raise KeyError(name)

    home_col = pick('home')
    away_col = pick('away')

    xg_cols = [c for c in df.columns if str(c).lower().startswith('xg')]
    if len(xg_cols) < 2:
        raise RuntimeError("Could not locate both xG columns on FBref schedule table")

    date_col = pick('date')

    score_col = None
    for c in df.columns:
        if str(c).lower().startswith('score'):
            score_col = c
            break

    out = pd.DataFrame({
        'date': pd.to_datetime(df[date_col], errors='coerce'),
        'home_team': df[home_col].astype(str),
        'away_team': df[away_col].astype(str),
        'home_xg': pd.to_numeric(df[xg_cols[0]], errors='coerce'),
        'away_xg': pd.to_numeric(df[xg_cols[1]], errors='coerce'),
        'score': df[score_col].astype(str) if score_col in df.columns else "",
    })

    def infer_status(score: str) -> str:
        s = score or ""
        return 'FINISHED' if re.search(r"\d+\s*[-–]\s*\d+", s) else 'SCHEDULED'

    out['status'] = out['score'].apply(infer_status)
    out = out.dropna(subset=['home_team', 'away_team'])
    return out
