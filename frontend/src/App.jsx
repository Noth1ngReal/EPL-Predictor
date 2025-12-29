import { useState } from 'react'
import CurrentMatchday from './components/CurrentMatchday'
import CustomPrediction from './components/CustomPrediction'
import './App.css'

function App() {
  const [activeView, setActiveView] = useState('current')

  const handleClearCache = () => {
    if (window.confirm('Clear all cached predictions? This will remove stored matchday and custom predictions.')) {
      localStorage.removeItem('epl_matchday_predictions')
      localStorage.removeItem('epl_custom_prediction')
      alert('Cache cleared! Reload the page to see changes.')
      window.location.reload()
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">
          <img
            src="/pl-logo.png"
            alt="Premier League Logo"
            className="pl-logo"
          />
          <h1 className="logo">EPL Predictor</h1>
          <p className="subtitle">ML-Powered Match Predictions</p>
        </div>

        <nav className="nav">
          <button
            className={`nav-item ${activeView === 'current' ? 'active' : ''}`}
            onClick={() => setActiveView('current')}
          >
            <span className="nav-text">Current Matchday</span>
          </button>

          <button
            className={`nav-item ${activeView === 'custom' ? 'active' : ''}`}
            onClick={() => setActiveView('custom')}
          >
            <span className="nav-text">Custom Prediction</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <button className="clear-cache-btn" onClick={handleClearCache}>
            Clear Cache
          </button>
        </div>
      </aside>

      <main className="main-content">
        {activeView === 'current' ? <CurrentMatchday /> : <CustomPrediction />}
      </main>
    </div>
  )
}

export default App
