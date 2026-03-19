TEAMNAME_MAP = {
    # football-data.org  -> Understat
    "Spurs": "Tottenham Hotspur",
    "Wolves": "Wolverhampton Wanderers",
    "Man United": "Manchester United",
    "Man City": "Manchester City",
    "Nott'm Forest": "Nottingham Forest",
    "Sheffield Utd": "Sheffield United",
    "Sheff Utd": "Sheffield United",
    "Brighton & Hove Albion": "Brighton",
    "Newcastle": "Newcastle United",
    "West Ham United": "West Ham",
}

def normalize_team(name: str) -> str:
    return TEAMNAME_MAP.get(name, name)
