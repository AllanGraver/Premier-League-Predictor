from __future__ import annotations

import os
import time
import requests
import pandas as pd

BASE_URL = "https://api.football-data.org/v4"


class FootballDataClient:
    def __init__(self, token: str, timeout: int = 30):
        if not token:
            raise ValueError("FOOTBALL_DATA_TOKEN mangler. Opret secret og sæt env var.")
        self.session = requests.Session()
        self.session.headers.update({"X-Auth-Token": token})
        self.timeout = timeout

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{BASE_URL}{path}"
        r = self.session.get(url, params=params, timeout=self.timeout)
        if r.status_code == 429:
            time.sleep(5)
            r = self.session.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def competition_matches(self, code: str, date_from: str, date_to: str) -> dict:
        return self._get(f"/competitions/{code}/matches", params={"dateFrom": date_from, "dateTo": date_to})


def matches_to_df(payload: dict) -> pd.DataFrame:
    matches = payload.get("matches", [])
    rows = []
    for m in matches:
        score = m.get("score", {}) or {}
        ft = (score.get("fullTime") or {})
        home = (m.get("homeTeam") or {})
        away = (m.get("awayTeam") or {})
        comp = (m.get("competition") or {})
        season = (m.get("season") or {})
        rows.append({
            "match_id": m.get("id"),
            "utcDate": m.get("utcDate"),
            "status": m.get("status"),
            "matchday": m.get("matchday"),
            "stage": m.get("stage"),
            "group": m.get("group"),
            "home_team": home.get("name"),
            "away_team": away.get("name"),
            "home_goals": ft.get("home"),
            "away_goals": ft.get("away"),
            "competition_code": comp.get("code"),
            "competition_name": comp.get("name"),
            "season_id": season.get("id"),
            "season_start": season.get("startDate"),
            "season_end": season.get("endDate"),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["utcDate"] = pd.to_datetime(df["utcDate"], utc=True, errors="coerce")
        df = df.sort_values("utcDate")
    return df


def fetch_matches(config: dict) -> pd.DataFrame:
    token = os.getenv("FOOTBALL_DATA_TOKEN", "").strip()
    client = FootballDataClient(token)
    code = config["competition_code"]
    payload = client.competition_matches(code, date_from=config["_date_from"], date_to=config["_date_to"])
    return matches_to_df(payload)
