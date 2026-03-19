from __future__ import annotations

import pandas as pd
import soccerdata as sd


def fetch_epl_schedule_with_xg() -> pd.DataFrame:
    """
    Hent EPL/PL kamp-program med xG via Understat (soccerdata).
    Returnerer et DataFrame med:
      date, home_team, away_team, home_xg, away_xg, status
    """

    league = "ENG-Premier League"  # Valid league name in soccerdata for PL [1](https://github.com/probberechts/soccerdata/blob/master/soccerdata/understat.py)

    us = sd.Understat(leagues=league)  # seasons=None => soccerdata vælger seneste sæsoner automatisk
    sched = us.read_schedule(include_matches_without_data=False)  # sikrer at xG-data findes [1](https://github.com/probberechts/soccerdata/blob/master/soccerdata/understat.py)

    # Understat.read_schedule() returnerer DF med index: ['league','season','game'] [1](https://github.com/probberechts/soccerdata/blob/master/soccerdata/understat.py)
    df = sched.reset_index()  # gør league/season/game til kolonner

    # Understat giver is_result (bool). Vi mapper til FINISHED/SCHEDULED så resten af pipeline passer. [1](https://github.com/probberechts/soccerdata/blob/master/soccerdata/understat.py)
    df["status"] = df["is_result"].map({True: "FINISHED", False: "SCHEDULED"})

    # Sørg for typer
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["home_xg"] = pd.to_numeric(df["home_xg"], errors="coerce")
    df["away_xg"] = pd.to_numeric(df["away_xg"], errors="coerce")

    return df[["date", "home_team", "away_team", "home_xg", "away_xg", "status"]]
