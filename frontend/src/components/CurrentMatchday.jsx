import { useState, useEffect } from "react";
import axios from "axios";
import PredictionCard from "./PredictionCard";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
const CACHE_KEY = "epl_matchday_predictions";
const CACHE_DURATION = 30 * 60 * 1000; // 30 min

function CurrentMatchday() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchPredictions = async (forceRefresh = false) => {
    if (!forceRefresh) {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        try {
          const { predictions: cachedPredictions, timestamp } =
            JSON.parse(cached);
          const age = Date.now() - timestamp;

          if (age < CACHE_DURATION) {
            console.log(
              `Using cached predictions (${Math.round(age / 60000)} minutes old)`,
            );
            setPredictions(cachedPredictions);
            setLastUpdated(new Date(timestamp));
            return;
          }
        } catch (e) {
          console.error("Error reading cache:", e);
        }
      }
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `${API_URL}/api/predictions/current-matchday`,
        {
          timeout: 120000,
        },
      );
      const newPredictions = response.data.predictions;
      const timestamp = Date.now();

      setPredictions(newPredictions);
      setLastUpdated(new Date(timestamp));

      localStorage.setItem(
        CACHE_KEY,
        JSON.stringify({
          predictions: newPredictions,
          timestamp,
        }),
      );

      console.log("Fetched and cached fresh predictions");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to fetch predictions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const cached = localStorage.getItem(CACHE_KEY);
    if (cached) {
      try {
        const { predictions: cachedPredictions, timestamp } =
          JSON.parse(cached);
        setPredictions(cachedPredictions);
        setLastUpdated(new Date(timestamp));
        console.log("Loaded cached predictions on mount");
      } catch (e) {
        console.error("Error reading cache:", e);
      }
    }
  }, []);

  const formatLastUpdated = () => {
    if (!lastUpdated) return "";
    const now = Date.now();
    const diff = now - lastUpdated.getTime();
    const minutes = Math.round(diff / 60000);

    if (minutes < 1) return "Updated just now";
    if (minutes === 1) return "Updated 1 minute ago";
    return `Updated ${minutes} minutes ago`;
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Current Matchday Predictions</h2>
          {lastUpdated && <p className="last-updated">{formatLastUpdated()}</p>}
        </div>
        {predictions.length > 0 && (
          <button
            className="refresh-btn"
            onClick={() => fetchPredictions(true)}
            disabled={loading}
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
        )}
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Fetching current matchday predictions...</p>
          <p className="loading-note">
            This may take 2-3 minutes due to API rate limits
          </p>
        </div>
      )}

      {!loading && predictions.length === 0 && !error && (
        <div className="empty-state">
          <button
            className="load-predictions-btn"
            onClick={() => fetchPredictions(false)}
          >
            Load Current Matchday Predictions
          </button>
        </div>
      )}

      <div className="predictions-grid">
        {predictions.map((pred, index) => (
          <PredictionCard
            key={index}
            homeTeam={pred.homeTeam}
            awayTeam={pred.awayTeam}
            probabilities={pred.probabilities}
            date={pred.date}
          />
        ))}
      </div>
    </div>
  );
}

export default CurrentMatchday;
