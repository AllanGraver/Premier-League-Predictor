from __future__ import annotations

import pandas as pd
import soccerdata as sd


def fetch_epl_schedule_with_xg() -> pd.DataFrame:
    """
    Fetch EPL schedule with xG from Understat via soccerdata.

    Returns a DataFrame that we will later normalize to:
    date, home_team, away_team, home_xg, away_xg, status
    """
    # 1) Get available seasons first
    us0 = sd.Understat(leagues="ENG-Premier League")
    seasons = us0.read_seasons()  # supported method [5](https://github.com/probberechts/soccerdata/blob/master/docs/reference/understat.rst)

    # Pick the latest season in the table (format depends on the source)
    # Commonly it's an int start-year.
    latest = seasons["season"].max()

    # 2) Fetch schedule for latest season (schedule includes xG) [3](https://deepwiki.com/probberechts/soccerdata/3.5-understat-and-sofascore-scrapers)[5](https://github.com/probberechts/soccerdata/blob/master/docs/reference/understat.rst)
    us = sd.Understat(leagues="ENG-Premier League", seasons=[latest])
    sched = us.read_schedule()

    # Inspect columns once locally if needed: print(sched.columns)
    # Normalize column names to what your pipeline expects
    out = sched.rename(
        columns={
            "date": "date",
            "home_team": "home_team",
            "away_team": "away_team",
            "home_xg": "home_xg",
            "away_xg": "away_xg",
            "status": "status",
        }
    ).copy()

    # Ensure correct types
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["home_xg"] = pd.to_numeric(out["home_xg"], errors="coerce")
    out["away_xg"] = pd.to_numeric(out["away_xg"], errors="coerce")

    # If statuses differ, map them here:
    # Some sources use "FT" etc. Adjust if needed after a first run.
    return out[["date", "home_team", "away_team", "home_xg", "away_xg", "status"]]
