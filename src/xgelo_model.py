from __future__ import annotations

import pandas as pd


def expected_score(r_a: float, r_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((r_b - r_a) / 400.0))


def actual_from_xg(home_xg: float, away_xg: float, xg_scale: float = 1.0) -> float:
    diff = float(home_xg) - float(away_xg)
    denom = (400.0 / 50.0) / max(1e-6, float(xg_scale))
    return 1.0 / (1.0 + 10 ** (-diff / denom))


def compute_xgelo(
    matches_xg_df: pd.DataFrame,
    home_advantage: float = 50.0,
    k_factor: float = 20.0,
    base_rating: float = 1500.0,
    xg_scale: float = 1.0,
) -> pd.DataFrame:
    df = matches_xg_df.copy()
    df = df[(df['status'] == 'FINISHED') & df['home_xg'].notna() & df['away_xg'].notna()]
    if df.empty:
        return pd.DataFrame(columns=['team', 'elo'])

    df = df.sort_values('date')
    ratings: dict[str, float] = {}

    for _, row in df.iterrows():
        h = row['home_team']
        a = row['away_team']
        hxg = float(row['home_xg'])
        axg = float(row['away_xg'])

        rh = ratings.get(h, base_rating) + home_advantage
        ra = ratings.get(a, base_rating)

        exp_home = expected_score(rh, ra)
        act_home = actual_from_xg(hxg, axg, xg_scale=xg_scale)

        new_rh = rh + k_factor * (act_home - exp_home)
        new_ra = ra + k_factor * ((1.0 - act_home) - (1.0 - exp_home))

        ratings[h] = new_rh - home_advantage
        ratings[a] = new_ra

    out = pd.DataFrame([{'team': t, 'elo': r} for t, r in ratings.items()])
    # rank_percentile bruges KUN til UI (stjerner), ikke i beregninger
    out = out.sort_values('elo', ascending=True).reset_index(drop=True)
    out['rank'] = out.index + 1
    N = len(out)
    out['rank_percentile'] = 1.0 - (out['rank'] - 1) / max(1, N-1)
    return out.sort_values('elo', ascending=False).reset_index(drop=True)
