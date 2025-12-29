import { useState, useEffect } from "react";
import axios from "axios";
import PredictionCard from "./PredictionCard";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
const CACHE_KEY = "epl_custom_prediction";

function CustomPrediction() {
  const [teams, setTeams] = useState([]);
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTeams();
    loadFromCache();
  }, []);

  const loadFromCache = () => {
    const cached = localStorage.getItem(CACHE_KEY);
    if (cached) {
      try {
        const {
          homeTeam: cachedHome,
          awayTeam: cachedAway,
          prediction: cachedPrediction,
        } = JSON.parse(cached);
        setHomeTeam(cachedHome || "");
        setAwayTeam(cachedAway || "");
        setPrediction(cachedPrediction || null);
        console.log("Loaded previous custom prediction from cache");
      } catch (e) {
        console.error("Error reading cache:", e);
      }
    }
  };

  const saveToCache = (home, away, pred) => {
    localStorage.setItem(
      CACHE_KEY,
      JSON.stringify({
        homeTeam: home,
        awayTeam: away,
        prediction: pred,
      }),
    );
  };

  const fetchTeams = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/teams`);
      setTeams(response.data.teams);
    } catch (err) {
      console.error("Failed to fetch teams:", err);
    }
  };

  const handlePredict = async () => {
    if (!homeTeam || !awayTeam) {
      setError("Please select both teams");
      return;
    }

    if (homeTeam === awayTeam) {
      setError("Please select different teams");
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await axios.post(`${API_URL}/api/predictions/custom`, {
        homeTeam,
        awayTeam,
      });
      const newPrediction = response.data;
      setPrediction(newPrediction);

      saveToCache(homeTeam, awayTeam, newPrediction);
      console.log("Saved custom prediction to cache");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to get prediction");
    } finally {
      setLoading(false);
    }
  };

  const handleSwap = () => {
    const temp = homeTeam;
    const newHome = awayTeam;
    const newAway = temp;
    setHomeTeam(newHome);
    setAwayTeam(newAway);
    setPrediction(null);

    saveToCache(newHome, newAway, null);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h2 className="view-title">Custom Match Prediction</h2>
      </div>

      <div className="custom-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="home-team">Home Team</label>
            <select
              id="home-team"
              value={homeTeam}
              onChange={(e) => {
                const newHome = e.target.value;
                setHomeTeam(newHome);
                setPrediction(null);
                saveToCache(newHome, awayTeam, null);
              }}
              className="team-select"
            >
              <option value="">Select home team...</option>
              {teams.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </div>

          <button className="swap-btn" onClick={handleSwap} title="Swap teams">
            ⇄
          </button>

          <div className="form-group">
            <label htmlFor="away-team">Away Team</label>
            <select
              id="away-team"
              value={awayTeam}
              onChange={(e) => {
                const newAway = e.target.value;
                setAwayTeam(newAway);
                setPrediction(null);
                saveToCache(homeTeam, newAway, null);
              }}
              className="team-select"
            >
              <option value="">Select away team...</option>
              {teams.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          className="predict-btn"
          onClick={handlePredict}
          disabled={loading || !homeTeam || !awayTeam}
        >
          {loading ? "Predicting..." : "Get Prediction"}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Fetching prediction...</p>
        </div>
      )}

      {prediction && !loading && (
        <div className="prediction-result">
          <PredictionCard
            homeTeam={prediction.homeTeam}
            awayTeam={prediction.awayTeam}
            probabilities={prediction.probabilities}
          />
        </div>
      )}
    </div>
  );
}

export default CustomPrediction;
