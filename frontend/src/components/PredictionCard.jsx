function PredictionCard({ homeTeam, awayTeam, probabilities, date }) {
  const maxProb = Math.max(
    probabilities.home,
    probabilities.draw,
    probabilities.away,
  );

  const getOutcome = () => {
    if (probabilities.home === maxProb) return "HOME";
    if (probabilities.away === maxProb) return "AWAY";
    return "DRAW";
  };

  const getConfidence = () => {
    if (maxProb > 0.5) return "High";
    if (maxProb > 0.4) return "Medium";
    return "Low";
  };

  return (
    <div className="prediction-card">
      <div className="card-header">
        <div className="teams">
          <span className="team-name">{homeTeam}</span>
          <span className="vs">vs</span>
          <span className="team-name">{awayTeam}</span>
        </div>
        {date && (
          <div className="match-date">
            {new Date(date).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>

      <div className="probabilities">
        <div className="prob-item">
          <div className="prob-label">
            <span>HOME WIN</span>
            <span className="prob-value">
              {(probabilities.home * 100).toFixed(1)}%
            </span>
          </div>
          <div className="prob-bar-container">
            <div
              className={`prob-bar home ${probabilities.home === maxProb ? "winner" : ""}`}
              style={{ width: `${probabilities.home * 100}%` }}
            />
          </div>
        </div>

        <div className="prob-item">
          <div className="prob-label">
            <span>DRAW</span>
            <span className="prob-value">
              {(probabilities.draw * 100).toFixed(1)}%
            </span>
          </div>
          <div className="prob-bar-container">
            <div
              className={`prob-bar draw ${probabilities.draw === maxProb ? "winner" : ""}`}
              style={{ width: `${probabilities.draw * 100}%` }}
            />
          </div>
        </div>

        <div className="prob-item">
          <div className="prob-label">
            <span>AWAY WIN</span>
            <span className="prob-value">
              {(probabilities.away * 100).toFixed(1)}%
            </span>
          </div>
          <div className="prob-bar-container">
            <div
              className={`prob-bar away ${probabilities.away === maxProb ? "winner" : ""}`}
              style={{ width: `${probabilities.away * 100}%` }}
            />
          </div>
        </div>
      </div>

      <div className="prediction-footer">
        <span className="prediction-label">Prediction:</span>
        <span className="prediction-outcome">{getOutcome()}</span>
        <span
          className={`confidence confidence-${getConfidence().toLowerCase()}`}
        >
          {getConfidence()} Confidence
        </span>
      </div>
    </div>
  );
}

export default PredictionCard;
