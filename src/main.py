from __future__ import annotations

import os
import yaml
import pandas as pd

from .utils import utc_today, iso
from .fetch_football_data import fetch_matches
from .xg_fbref import fetch_pl_schedule_with_xg
from .xgelo_model import compute_xgelo
from .predict import make_predictions
from .ui_format import fav_label, upset_icon


def load_config(path: str = "config.yml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def predictions_to_markdown_s1(pred_df: pd.DataFrame, cfg: dict, title: str = "Premier League – næste uges kampe") -> str:
    ui = (cfg.get('ui') or {})
    traffic = (ui.get('traffic_light') or {})
    upset = (ui.get('upset') or {})

    if pred_df.empty:
        return f"# {title}

Ingen kommende kampe fundet i perioden.
"

    lines = [f"# {title} (Sejrschancer + Trafiklys + Top-scorelines)", "", f"Genereret: {pd.Timestamp.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ""]

    for _, r in pred_df.iterrows():
        dt = pd.to_datetime(r["utcDate"]).strftime("%Y-%m-%d %H:%M UTC") if pd.notna(r["utcDate"]) else ""
        p_home, p_draw, p_away = float(r['p_home']), float(r['p_draw']), float(r['p_away'])
        emoji, label = fav_label(p_home, p_away, strong_gap=float(traffic.get('strong_gap', 0.20))) if traffic.get('enabled', True) else ("","")
        warn = upset_icon(p_home, p_away, thr=float(upset.get('threshold', 0.30))) if upset.get('enabled', True) else ""

        lines.append(f"## {r['home_team']} vs {r['away_team']} ({dt})")
        lines.append(f"**Chancer:** {('🟩' if p_home>p_away else '🟥') if emoji else ''} Hjemme {p_home*100:.0f}%  |  🟨 Uafgjort {p_draw*100:.0f}%  |  {('🟥' if p_home>p_away else '🟩') if emoji else ''} Ude {p_away*100:.0f}%")
        if emoji or warn or label:
            tag = f"{warn} {emoji} {label}".strip()
            if tag:
                lines.append(f"**Kampbillede:** {tag}")
        # Top scorelines
        tops = []
        for i in [1,2,3]:
            s = r.get(f"top{i}", "")
            pr = r.get(f"top{i}_p", "")
            if s:
                tops.append(f"{i}) {s} (p≈{float(pr)*100:.1f}%)")
        if tops:
            lines.append("**Top scorelines:** " + " | ".join(tops))
        lines.append(f"**Forventede mål (λ):** hjemme={r['lambda_home']}, ude={r['lambda_away']}")
        lines.append("")

    return "
".join(lines) + "
"


def main() -> None:
    cfg = load_config()

    today = utc_today()
    days_back = int(cfg.get("days_back", 365))
    days_forward = int(cfg.get("days_forward", 7))

    date_from = today - pd.Timedelta(days=days_back)
    date_to = today + pd.Timedelta(days=days_forward)

    cfg["_date_from"] = iso(date_from)
    cfg["_date_to"] = iso(date_to)

    # 1) FBref xG historik
    pl_xg = fetch_pl_schedule_with_xg()
    xg_hist = pl_xg[(pl_xg['status'] == 'FINISHED') & (pl_xg['date'] >= pd.to_datetime(date_from))]

    # 2) Officielle fixtures (næste uge)
    matches_df = fetch_matches(cfg).sort_values('utcDate')

    # 3) Gem matches
    matches_path = cfg['outputs']['matches_csv']
    ensure_parent(matches_path)
    if os.path.exists(matches_path):
        old = pd.read_csv(matches_path, parse_dates=['utcDate'])
        matches_df = pd.concat([old, matches_df], ignore_index=True)
        matches_df = matches_df.drop_duplicates(subset=['match_id'], keep='last')
        matches_df = matches_df.sort_values('utcDate')
    matches_df.to_csv(matches_path, index=False)

    # 4) xGElo ratings (m/ rank_percentile til ev. UI)
    xg_scale = float((cfg.get('xgelo') or {}).get('xg_scale', 1.0))
    elo_df = compute_xgelo(
        xg_hist[['date', 'home_team', 'away_team', 'home_xg', 'away_xg', 'status']],
        home_advantage=float(cfg.get('home_advantage', 50)),
        k_factor=float(cfg.get('k_factor', 20)),
        base_rating=1500.0,
        xg_scale=xg_scale,
    )

    elo_path = cfg['outputs']['elo_csv']
    ensure_parent(elo_path)
    elo_df.to_csv(elo_path, index=False)

    # 5) Predictions + Scenario 1 rapport
    max_goals = int((cfg.get('prediction') or {}).get('max_goals', 6))
    top_n = int((cfg.get('prediction') or {}).get('top_n_scorelines', 3))

    pred_df = make_predictions(
        matches_df,
        elo_df,
        home_advantage=float(cfg.get('home_advantage', 50)),
        max_goals=max_goals,
        top_n_scorelines=top_n,
    )

    pred_csv = cfg['outputs']['predictions_csv']
    ensure_parent(pred_csv)
    pred_df.to_csv(pred_csv, index=False)

    pred_md_path = cfg['outputs']['predictions_md']
    ensure_parent(pred_md_path)
    with open(pred_md_path, 'w', encoding='utf-8') as f:
        f.write(predictions_to_markdown_s1(pred_df, cfg))

    print('✅ Daily update complete (UI Scenario 1)')
    print(f"- xG matches (hist window): {len(xg_hist)}")
    print(f"- next-week predictions: {len(pred_df)}")


if __name__ == "__main__":
    main()
