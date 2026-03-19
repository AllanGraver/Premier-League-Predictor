TEAMNAME_MAP = {
    # football-data.org  -> Understat
    "Arsenal FC": "Arsenal",
    "Brentford FC": "Brentford",
    "Brighton & Hove Albion FC": "Brighton",
    "Burnley FC": "Burnley",
    "Chelsea FC": "Chelsea",
    "Crystal Palace FC": "Crystal Palace",
    "AFC Bournemouth": "Bournemouth",
    "Aston Villa FC": "Aston Villa",
    "Everton FC": "Everton",
    "Fulham FC": "Fulham",
    "Leeds United FC": "Leeds",
    "Liverpool FC": "Liverpool",
    "Manchester United FC": "Manchester United",
    "Manchester City FC": "Manchester City",
    "Newcastle United": "Newcastle United",
    "Nottingham Forest FC": "Nottingham Forest",
    "Sunderland AFC": "Sunderland",
    "Tottenham Hotspur FC": "Tottenham",
    "West Ham United FC": "West Ham",
    "Wolverhampton Wanderers FC": "Wolverhampton Wanderers",
    }

def normalize_team(name: str) -> str:
    return TEAMNAME_MAP.get(name, name)
