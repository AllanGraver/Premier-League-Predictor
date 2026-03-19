from __future__ import annotations

def fav_label(p_home: float, p_away: float, strong_gap: float = 0.20):
    gap = abs(p_home - p_away)
    if gap >= strong_gap:
        return ("🟩", "Klar hjemmefavorit") if p_home > p_away else ("🟥", "Klar udefavorit")
    return ("🟨", "Åben kamp")


def upset_icon(p_home: float, p_away: float, thr: float = 0.30) -> str:
    underdog = min(p_home, p_away)
    return "⚠️" if underdog >= thr else ""
