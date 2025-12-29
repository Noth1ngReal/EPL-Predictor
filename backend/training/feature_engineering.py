import pandas as pd


def calculate_team_stats(df, team, date, venue_type):
    mask = (df["team"] == team) & (df["date"] < date) & (df["venue"] == venue_type)
    team_matches = df[mask]

    if len(team_matches) == 0:
        return {"goals_per_game": 1.5, "goals_conceded_per_game": 1.5, "win_rate": 0.33}

    return {
        "goals_per_game": team_matches["gf"].mean(),
        "goals_conceded_per_game": team_matches["ga"].mean(),
        "win_rate": (team_matches["result"] == "W").sum() / len(team_matches),
    }


def calculate_recent_form(df, team, date):
    mask = (df["team"] == team) & (df["date"] < date)
    recent = df[mask].tail(5)

    if len(recent) == 0:
        return 0.5

    points = recent["result"].map({"W": 3, "D": 1, "L": 0}).sum()
    return points / (len(recent) * 3)


print("Loading data...")
df = pd.read_csv("ml_training/data/raw/matches.csv")
df["date"] = pd.to_datetime(df["date"])
df = df[df["comp"] == "Premier League"].copy()
df = df.sort_values("date").reset_index(drop=True)

print(f"Total matches: {len(df)}")
print("Extracting features...")

features_list = []
home_matches = df[df["venue"] == "Home"].copy()

print(f"Home matches to process: {len(home_matches)}")

for idx, match in home_matches.iterrows():
    if idx < 5:
        print(f"Processing match {idx}: {match['team']} vs {match['opponent']}")

    home_team = match["team"]
    away_team = match["opponent"]
    match_date = match["date"]

    home_stats = calculate_team_stats(df, home_team, match_date, "Home")
    away_stats = calculate_team_stats(df, away_team, match_date, "Away")
    home_form = calculate_recent_form(df, home_team, match_date)
    away_form = calculate_recent_form(df, away_team, match_date)

    if match["result"] == "W":
        outcome = "HOME"
    elif match["result"] == "D":
        outcome = "DRAW"
    else:
        outcome = "AWAY"

    features_list.append(
        {
            "home_goals_per_game": home_stats["goals_per_game"],
            "away_goals_per_game": away_stats["goals_per_game"],
            "home_goals_conceded_per_game": home_stats["goals_conceded_per_game"],
            "away_goals_conceded_per_game": away_stats["goals_conceded_per_game"],
            "home_win_rate": home_stats["win_rate"],
            "away_win_rate": away_stats["win_rate"],
            "home_recent_form": home_form,
            "away_recent_form": away_form,
            "outcome": outcome,
        }
    )

    if (idx + 1) % 100 == 0:
        print(
            f"Processed {idx + 1}/{len(home_matches)}, features list has {len(features_list)} rows"
        )

print(f"Loop finished. Features list length: {len(features_list)}")

features_df = pd.DataFrame(features_list)
print(f"\nTotal rows: {len(features_df)}")
print("\nOutcome distribution:")
print(features_df["outcome"].value_counts(normalize=True))

features_df.to_csv("ml_training/data/processed/features_dataset.csv", index=False)
print("\nSaved to ml_training/data/processed/features_dataset.csv")
