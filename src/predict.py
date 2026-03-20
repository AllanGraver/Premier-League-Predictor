from __future__ import annotations

import math
import pandas as pd


def poisson_pmf(lmbda: float, k: int) -> float:
    if lmbda <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lmbda) * (lmbda ** k) / math.factorial(k)


def scoreline_grid(lh: float, la: float, max_goals: int = 6):
    grid = []
    for hg in range(0, max_goals + 1):
        ph = poisson_pmf(lh, hg)
        for ag in range(0, max_goals + 1):
            pa = poisson_pmf(la, ag)
            grid.append(((hg, ag), ph * pa))
    return grid


def outcome_probs_and_top_scorelines(lh: float, la: float, max_goals: int = 6, top_n: int = 3):
    grid = scoreline_grid(lh, la, max_goals=max_goals)

    p_home = p_draw = p_away = 0.0
    total = 0.0
    for (hg, ag), p in grid:
        total += p
        if hg > ag:
            p_home += p
        elif hg < ag:
            p_away += p
        else:
            p_draw += p

    if total > 0:
        p_home, p_draw, p_away = p_home / total, p_draw / total, p_away / total

    top = sorted(grid, key=lambda x: x[1], reverse=True)[:max(1, int(top_n))]
    top_fmt = [{"hg": hg, "ag": ag, "prob": p / total} for (hg, ag), p in top]

    return p_home, p_draw, p_away, top_fmt


def league_goal_baseline(matches_df: pd.DataFrame):
    finished = matches_df[(matches_df["status"] == "FINISHED") & matches_df["home_goals"].notna() & matches_df["away_goals"].notna()].copy()
   
    if finished.empty:
        # fallback: brug samme baseline for hjemme/ude
        base = 1.25
        return base, base

    base = (float(finished["home_goals"].astype(float).mean())
            + float(finished["away_goals"].astype(float).mean())) / 2.0

    return base, base



def elo_to_goal_means(elo_home: float, elo_away: float, base_home: float, base_away: float, home_advantage: float = 50.0, alpha: float = 0.70):
    adj_home = elo_home + home_advantage
    diff = adj_home - elo_away
    strength = 10 ** (diff / 400.0)
    s = strength ** alpha
    lh = base_home * math.sqrt(s)
    la = base_away / math.sqrt(s)
    return max(0.2, lh), max(0.2, la)


def make_predictions(matches_df: pd.DataFrame, elo_df: pd.DataFrame, home_advantage: float = 50.0, max_goals: int = 6, top_n_scorelines: int = 3) -> pd.DataFrame:
    upcoming = matches_df[matches_df["status"].isin(["SCHEDULED", "TIMED"])].copy()
    if upcoming.empty:
        return pd.DataFrame(columns=["utcDate","home_team","away_team","p_home","p_draw","p_away","predicted_result"])

    ratings = dict(zip(elo_df["team"], elo_df["elo"]))
    base_home, base_away = league_goal_baseline(matches_df)

    rows = []
    for _, r in upcoming.iterrows():
        h = r["home_team"]
        a = r["away_team"]
        elo_h = float(ratings.get(h, 1500.0))
        elo_a = float(ratings.get(a, 1500.0))

        lh, la = elo_to_goal_means(elo_h, elo_a, base_home, base_away, home_advantage=home_advantage)
        p_home, p_draw, p_away, top = outcome_probs_and_top_scorelines(lh, la, max_goals=max_goals, top_n=top_n_scorelines)

        best = top[0]
        predicted_result = f"{best['hg']}-{best['ag']}"

        def s(i):
            return f"{top[i]['hg']}-{top[i]['ag']}" if i < len(top) else ""
        def sp(i):
            return round(float(top[i]['prob']), 4) if i < len(top) else ""

        rows.append({
            "utcDate": r["utcDate"],
            "competition_code": r.get("competition_code"),
            "matchday": r.get("matchday"),
            "home_team": h,
            "away_team": a,
            "lambda_home": round(lh, 3),
            "lambda_away": round(la, 3),
            "p_home": round(p_home, 4),
            "p_draw": round(p_draw, 4),
            "p_away": round(p_away, 4),
            "predicted_result": predicted_result,
            "top1": s(0), "top1_p": sp(0),
            "top2": s(1), "top2_p": sp(1),
            "top3": s(2), "top3_p": sp(2),
        })

    return pd.DataFrame(rows).sort_values("utcDate")
