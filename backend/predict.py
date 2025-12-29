import pickle

import numpy as np

from api_client import get_match_features

print("Loading model and scaler...")
with open("ml_training/models/soccer_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("ml_training/models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

print("Model loaded successfully\n")


def predict_match(home_team_id, away_team_id):
    # Make prediction for a match using live API data"""
    print(f"Fetching features for match...")
    features, home_name, away_name = get_match_features(home_team_id, away_team_id)

    print(f"\nMatch: {home_name} (home) vs {away_name} (away)")
    print("\nRaw features:")
    feature_names = [
        "Home goals/game",
        "Away goals/game",
        "Home conceded/game",
        "Away conceded/game",
        "Home win rate",
        "Away win rate",
        "Home recent form",
        "Away recent form",
    ]
    for name, value in zip(feature_names, features):
        print(f"  {name}: {value:.3f}")

    features_array = np.array([features])
    features_scaled = scaler.transform(features_array)

    prediction = model.predict(features_scaled)[0]
    probabilities = model.predict_proba(features_scaled)[0]

    class_labels = model.classes_
    prob_dict = dict(zip(class_labels, probabilities))

    print(f"\nPrediction: {prediction}")
    print(f"\nProbabilities:")
    print(f"  HOME win: {prob_dict.get('HOME', 0):.1%}")
    print(f"  DRAW:     {prob_dict.get('DRAW', 0):.1%}")
    print(f"  AWAY win: {prob_dict.get('AWAY', 0):.1%}")

    return prediction, prob_dict
