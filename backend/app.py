import os
import pickle
import time
import warnings

import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

from api_client import BASE_URL, HEADERS, get_match_features

# suppress error msg
warnings.filterwarnings("ignore", message="X does not have valid feature names")

app = Flask(__name__)
CORS(app)

print("Loading model and scaler...")
with open("models/soccer_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

print("Model loaded successfully!")


def fetch_current_teams():
    """Fetch current Premier League teams from API"""
    try:
        url = f"{BASE_URL}/competitions/PL/standings"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Warning: Could not fetch teams from API, using fallback")
            return {}

        data = response.json()
        team_map = {}

        for team_data in data["standings"][0]["table"]:
            team_name = team_data["team"]["name"]
            team_id = team_data["team"]["id"]
            team_map[team_name] = team_id

        print(f"Loaded {len(team_map)} current Premier League teams from API")
        return team_map
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return {}


TEAM_ID_MAP = fetch_current_teams()


def predict_match_outcome(home_team_id, away_team_id, standings=None, form_cache=None):
    features, home_name, away_name = get_match_features(
        home_team_id, away_team_id, standings, form_cache
    )

    features_array = np.array([features])
    features_scaled = scaler.transform(features_array)

    prediction = model.predict(features_scaled)[0]
    probabilities = model.predict_proba(features_scaled)[0]

    class_labels = model.classes_
    prob_dict = dict(zip(class_labels, probabilities))

    return {
        "homeTeam": home_name,
        "awayTeam": away_name,
        "prediction": prediction,
        "probabilities": {
            "home": float(prob_dict.get("HOME", 0)),
            "draw": float(prob_dict.get("DRAW", 0)),
            "away": float(prob_dict.get("AWAY", 0)),
        },
    }


@app.route("/api/teams", methods=["GET"])
def get_teams():
    teams = sorted(list(TEAM_ID_MAP.keys()))
    return jsonify({"teams": teams})


@app.route("/api/predictions/custom", methods=["POST"])
def custom_prediction():
    data = request.json
    home_team = data.get("homeTeam")
    away_team = data.get("awayTeam")

    if not home_team or not away_team:
        return jsonify({"error": "Both teams required"}), 400

    if home_team == away_team:
        return jsonify({"error": "Teams must be different"}), 400

    if home_team not in TEAM_ID_MAP or away_team not in TEAM_ID_MAP:
        return jsonify({"error": "Invalid team"}), 400

    try:
        result = predict_match_outcome(TEAM_ID_MAP[home_team], TEAM_ID_MAP[away_team])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predictions/current-matchday", methods=["GET"])
def current_matchday():
    try:
        url = f"{BASE_URL}/competitions/PL/matches"
        params = {"status": "SCHEDULED"}
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch matches"}), 500

        matches = response.json().get("matches", [])

        print("Fetching standings once for all matches...")
        from api_client import fetch_standings

        standings = fetch_standings()

        form_cache = {}

        predictions = []
        for idx, match in enumerate(matches[:10]):
            home_id = match["homeTeam"]["id"]
            away_id = match["awayTeam"]["id"]

            try:
                result = predict_match_outcome(home_id, away_id, standings, form_cache)
                result["date"] = match["utcDate"]
                predictions.append(result)

                if idx < len(matches[:10]) - 1:
                    print(f"Processed {idx + 1}/10 matches, waiting 6 seconds...")
                    time.sleep(6)
            except Exception as e:
                print(f"Error predicting match {idx + 1}: {e}")
                continue

        print(f"Successfully predicted {len(predictions)} matches")
        return jsonify({"predictions": predictions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
