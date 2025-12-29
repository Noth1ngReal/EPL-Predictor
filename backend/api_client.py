import json
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

HEADERS = {"X-Auth-Token": API_KEY}


# 429 status = rate limited
def make_api_request(url, headers, params=None, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response

        if response.status_code == 429:
            try:
                error_data = response.json()
                error_msg = error_data.get("message", "")
                if "Wait" in error_msg and "seconds" in error_msg:
                    wait_time = int(
                        error_msg.split("Wait")[1].split("seconds")[0].strip()
                    )
                    print(
                        f"Rate limit hit. Waiting {wait_time} seconds before retry..."
                    )
                    time.sleep(wait_time + 2)
                    continue
            except:
                print(f"Rate limit hit. Waiting 60 seconds before retry...")
                time.sleep(60)
                continue

        raise Exception(f"API error: {response.status_code} - {response.text}")

    raise Exception(f"Max retries ({max_retries}) exceeded for {url}")


def fetch_standings():
    """Fetch current Premier League standings"""
    url = f"{BASE_URL}/competitions/PL/standings"
    response = make_api_request(url, HEADERS)

    data = response.json()
    standings = {}

    for team_data in data["standings"][0]["table"]:
        team_id = team_data["team"]["id"]
        team_name = team_data["team"]["name"]

        standings[team_id] = {
            "name": team_name,
            "played": team_data["playedGames"],
            "won": team_data["won"],
            "goals_for": team_data["goalsFor"],
            "goals_against": team_data["goalsAgainst"],
        }

    return standings


def fetch_recent_matches(team_id, limit=5):
    url = f"{BASE_URL}/teams/{team_id}/matches"
    params = {"limit": limit, "status": "FINISHED"}

    response = make_api_request(url, HEADERS, params=params)

    data = response.json()
    return data["matches"]


def calculate_recent_form(team_id, form_cache=None):
    # Check cache first
    if form_cache is not None and team_id in form_cache:
        print(f"  → Using cached form for team {team_id}")
        return form_cache[team_id]

    print(f"  → Fetching recent matches from API for team {team_id}")
    matches = fetch_recent_matches(team_id, limit=5)

    if len(matches) == 0:
        form_value = 0.5
    else:
        points = 0
        for match in matches:
            home_id = match["homeTeam"]["id"]
            away_id = match["awayTeam"]["id"]
            home_score = match["score"]["fullTime"]["home"]
            away_score = match["score"]["fullTime"]["away"]

            if team_id == home_id:
                if home_score > away_score:
                    points += 3
                elif home_score == away_score:
                    points += 1
            else:
                if away_score > home_score:
                    points += 3
                elif home_score == away_score:
                    points += 1

        max_points = len(matches) * 3
        form_value = points / max_points

    if form_cache is not None:
        form_cache[team_id] = form_value

    return form_value


# extract all 8 features from matches
def get_match_features(home_team_id, away_team_id, standings=None, form_cache=None):
    if standings is None:
        print(f"Fetching standings...")
        standings = fetch_standings()

    if home_team_id not in standings or away_team_id not in standings:
        raise Exception("Team not found in standings")

    home_stats = standings[home_team_id]
    away_stats = standings[away_team_id]

    home_played = home_stats["played"]
    away_played = away_stats["played"]

    if home_played == 0 or away_played == 0:
        raise Exception("Team has not played any matches yet")

    home_goals_per_game = home_stats["goals_for"] / home_played
    away_goals_per_game = away_stats["goals_for"] / away_played
    home_conceded_per_game = home_stats["goals_against"] / home_played
    away_conceded_per_game = away_stats["goals_against"] / away_played
    home_win_rate = home_stats["won"] / home_played
    away_win_rate = away_stats["won"] / away_played

    # Calculate recent form (with caching inside calculate_recent_form)
    print(f'Getting recent form for {home_stats["name"]}...')
    home_form = calculate_recent_form(home_team_id, form_cache)

    print(f'Getting recent form for {away_stats["name"]}...')
    away_form = calculate_recent_form(away_team_id, form_cache)

    features = [
        home_goals_per_game,
        away_goals_per_game,
        home_conceded_per_game,
        away_conceded_per_game,
        home_win_rate,
        away_win_rate,
        home_form,
        away_form,
    ]

    return features, home_stats["name"], away_stats["name"]
