import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const TABS = [
  { id: 'current', label: 'This Week \ud83c\udfc8' },
  { id: 'past', label: 'Last Week Results \u23f3' },
];

const formatDate = (isoDate) => {
  if (!isoDate) {
    return 'TBD';
  }

  const parsed = new Date(isoDate);
  if (Number.isNaN(parsed.getTime())) {
    return isoDate;
  }

  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
  }).format(parsed);
};

const formatPercent = (value) => {
  if (value === null || value === undefined) {
    return '—';
  }
  return `${(value * 100).toFixed(1)}%`;
};

const probabilityWidth = (value) => {
  if (value === null || value === undefined) {
    return '0%';
  }
  return `${Math.max(10, Math.round(value * 100))}%`;
};

const confidenceClass = (label) => {
  if (!label) {
    return 'confidence-pill';
  }
  return `confidence-pill ${label.toLowerCase()}`;
};

const formatSpreadLine = (game) => {
  if (!game) {
    return null;
  }
  if (game.is_pick_em === true) {
    return 'Line: Pick’em';
  }
  if (game.favorite_team && game.spread_margin !== null && game.spread_margin !== undefined) {
    const favName = game.favorite_side === 'home' ? game.home_team : game.away_team;
    return `Line: ${favName} -${Number(game.spread_margin).toFixed(1)}`;
  }
  return null;
};

function MetricsPanel({ metrics }) {
  if (!metrics) {
    return null;
  }

  const overall = metrics.overall ?? {};
  const lifetimeAccuracy = overall.overall_accuracy ?? null;
  const totalPredictions = overall.total_predictions ?? 0;
  const correctPredictions = overall.correct_predictions ?? 0;
  const ensembleAccuracy = overall.ensemble_accuracy ?? null;
  const recentAccuracy = metrics.recent_accuracy ?? null;
  const recentSample = metrics.recent_sample_size ?? 0;
  const weekly = metrics.weekly_breakdown ?? [];
  const streak = metrics.current_streak;

  return (
    <section className="metrics-panel" aria-label="Model performance overview">
      <div className="metrics-grid">
        <div className="metric-card primary">
          <span className="metric-title">Lifetime Accuracy</span>
          <span className="metric-value">{formatPercent(lifetimeAccuracy)}</span>
          <span className="metric-sub">{correctPredictions}/{totalPredictions} games</span>
        </div>
        <div className="metric-card">
          <span className="metric-title">Recent Form</span>
          <span className="metric-value">{formatPercent(recentAccuracy)}</span>
          <span className="metric-sub">Last {recentSample} games</span>
        </div>
        <div className="metric-card">
          <span className="metric-title">Ensemble Accuracy</span>
          <span className="metric-value">{formatPercent(ensembleAccuracy)}</span>
          <span className="metric-sub">Across all models</span>
        </div>
        <div className="metric-card secondary">
          <span className="metric-title">Total Predictions</span>
          <span className="metric-value">{totalPredictions}</span>
          {streak ? (
            <span className={`metric-streak ${streak.type}`}>
              {streak.type === 'win' ? 'Win streak' : 'Skid'}: {streak.length}
            </span>
          ) : (
            <span className="metric-sub muted">Streak data pending</span>
          )}
        </div>
      </div>

      {weekly.length > 0 ? (
        <div className="weekly-panel">
          <h3>Recent Weeks</h3>
          <div className="weekly-list">
            {weekly.map((week) => (
              <div className="weekly-item" key={`${week.season}-${week.week}`}>
                <span className="weekly-week">W{week.week} · {week.season}</span>
                <span className="weekly-accuracy">{formatPercent(week.accuracy)}</span>
                <span className="weekly-record">{week.correct}/{week.total}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function UpsetWatchPanel({ summary }) {
  const games = summary?.upsets ?? [];

  if (!summary) {
    return null;
  }

  if (games.length === 0) {
    return (
      <section className="upset-panel" aria-label="Upset watch">
        <div className="upset-header">
          <h3>🚨 Upset Watch</h3>
          <span className="upset-subtitle">No underdog picks highlighted yet.</span>
        </div>
      </section>
    );
  }

  return (
    <section className="upset-panel" aria-label="Upset watch">
      <div className="upset-header">
        <h3>🚨 Upset Watch</h3>
        <span className="upset-subtitle">Model-backed underdogs with the strongest confidence</span>
      </div>
      <div className="upset-grid">
        {games.map((game) => {
          const bucketLabel = game?.confidence_bucket?.label ?? 'Unknown';
          const lineText = formatSpreadLine(game);
          return (
            <article className="upset-card" key={game.game_id}>
              <div className="upset-matchup">
                <span>{game.away_team} @ {game.home_team}</span>
                <span className={confidenceClass(bucketLabel)}>{bucketLabel} confidence</span>
              </div>
              {lineText ? <div className="upset-line">{lineText}</div> : null}
              <div className="upset-pick">
                <strong>{game.predicted_winner}</strong>
                <span className="upset-prob">{formatPercent(game.win_probability)}</span>
              </div>
              {game.reasoning ? (
                <p className="upset-reason">{game.reasoning}</p>
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function GameCard({ game, mode }) {
  const isPast = mode === 'past';
  const statusClass = isPast
    ? game.correct_prediction
      ? 'game-card past correct'
      : 'game-card past incorrect'
    : 'game-card upcoming';

  const bucketLabel = game?.confidence_bucket?.label ?? 'Unknown';
  const badgesClass = confidenceClass(bucketLabel);
  const spreadLine = formatSpreadLine(game);
  const showUnderdog = Boolean(game.is_underdog_pick);
  const underdogMargin = game.spread_margin !== null && game.spread_margin !== undefined
    ? `+${Number(game.spread_margin).toFixed(1)}`
    : null;

  return (
    <div className={statusClass}>
      <div className="game-header">
        <div className="game-meta">
          <span className="week-tag">Week {game.week}</span>
          <span className="date-tag">{formatDate(game.game_date)}</span>
        </div>
        {game.espn_url ? (
          <a className="espn-link" href={game.espn_url} target="_blank" rel="noopener noreferrer">
            View on ESPN
          </a>
        ) : null}
      </div>

      <div className="game-badges">
        <span className={badgesClass}>{bucketLabel} confidence</span>
        {showUnderdog ? (
          <span className="underdog-pill">
            Upset pick{underdogMargin ? ` • ${underdogMargin}` : ''}
          </span>
        ) : null}
      </div>

      <div className="teams">
        <div className={`team home ${game.predicted_winner === game.home_team ? 'winner' : 'loser'}`}>
          <span className="team-label">Home</span>
          <span className="team-name">{game.home_team}</span>
          {isPast && (
            <span className="team-score">{game.home_score ?? '—'}</span>
          )}
        </div>

        <div className="vs">vs</div>

        <div className={`team away ${game.predicted_winner === game.away_team ? 'winner' : 'loser'}`}>
          <span className="team-label">Away</span>
          <span className="team-name">{game.away_team}</span>
          {isPast && (
            <span className="team-score">{game.away_score ?? '—'}</span>
          )}
        </div>
      </div>

      {(spreadLine || showUnderdog) ? (
        <div className="matchup-context">
          {spreadLine ? <span>{spreadLine}</span> : null}
          {showUnderdog ? (
            <span>
              Model siding with {game.predicted_winner} despite the market.
            </span>
          ) : null}
        </div>
      ) : null}

      <div className="prediction-row">
        <span className="prediction-label">Bot Prediction</span>
        <div className="prediction-value">
          <span className="predicted-winner">{game.predicted_winner}</span>
          <span className="probability">{formatPercent(game.win_probability)}</span>
        </div>
      </div>

      <div className="confidence-bar">
        <div className="confidence-fill" style={{ width: probabilityWidth(game.confidence_score ?? game.win_probability) }} />
      </div>

      {game.reasoning && (
        <div className="reasoning-row">
          <span className="reasoning-label">📊 Why {game.predicted_winner}?</span>
          <div className="reasoning-text">{game.reasoning}</div>
        </div>
      )}

      {isPast ? (
        <div className="outcome-row">
          <span className="outcome-label">Final</span>
          <span className="outcome-value">{game.actual_winner ?? 'Pending'}{game.actual_winner ? '' : ' (TBC)'}</span>
        </div>
      ) : (
        <div className="outcome-row pending">
          <span className="outcome-label">Status</span>
          <span className="outcome-value">Awaiting kickoff</span>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('current');
  const [currentPredictions, setCurrentPredictions] = useState([]);
  const [pastPredictions, setPastPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState({ current: {}, past: {} });
  const [selectedSeason, setSelectedSeason] = useState(2025);
  const [selectedWeek, setSelectedWeek] = useState(6);
  const [accuracyStats, setAccuracyStats] = useState(null);
  const [metricsOverview, setMetricsOverview] = useState(null);
  const [upsetSummary, setUpsetSummary] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [currentResponse, pastResponse, metricsResponse, upsetResponse] = await Promise.all([
          axios.get(`${API_BASE_URL}/predictions/current`, {
            params: { season: selectedSeason, week: selectedWeek }
          }),
          axios.get(`${API_BASE_URL}/predictions/past`),
          axios.get(`${API_BASE_URL}/metrics/overview`),
          axios.get(`${API_BASE_URL}/insights/upsets`, {
            params: { season: selectedSeason, week: selectedWeek, limit: 4 }
          }),
        ]);

        const currentData = currentResponse.data ?? {};
        const pastData = pastResponse.data ?? {};
        const metricsData = metricsResponse.data ?? null;
        const upsetData = upsetResponse.data ?? null;

        setCurrentPredictions(currentData.predictions ?? []);
        setPastPredictions(pastData.predictions ?? []);
        setAccuracyStats(pastData.accuracy_stats ?? null);
        setMetadata({
          current: { season: currentData.season, week: currentData.week },
          past: { season: pastData.season, week: pastData.week },
        });
        setMetricsOverview(metricsData);
        setUpsetSummary(upsetData);
      } catch (err) {
        setError(err.message ?? 'Failed to load predictions.');
        setMetricsOverview(null);
        setUpsetSummary(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedSeason, selectedWeek]);

  const pageTitle = useMemo(() => {
    if (activeTab === 'current') {
      const info = metadata.current;
      if (info?.season && info?.week) {
        return `Upcoming Predictions • ${info.season} Season Week ${info.week}`;
      }
      return 'Upcoming Predictions';
    }

    const info = metadata.past;
    if (info?.season && info?.week) {
      return `Last Week Recap • ${info.season} Season Week ${info.week}`;
    }
    return 'Last Week Recap';
  }, [activeTab, metadata]);

  const renderContent = () => {
    if (loading) {
      return <div className="status-message">Loading predictions...</div>;
    }

    if (error) {
      return <div className="status-message error">{error}</div>;
    }

    if (activeTab === 'current') {
      const upcomingBody = currentPredictions.length === 0 ? (
        <div className="status-message">No upcoming predictions at the moment.</div>
      ) : (
        <div className="grid">
          {currentPredictions.map((game) => (
            <GameCard key={game.game_id} game={game} mode="current" />
          ))}
        </div>
      );

      return (
        <>
          <UpsetWatchPanel summary={upsetSummary} />
          {upcomingBody}
        </>
      );
    }

    if (pastPredictions.length === 0) {
      return <div className="status-message">No completed predictions to display yet.</div>;
    }

    return (
      <>
        {accuracyStats && accuracyStats.total_evaluated > 0 && (
          <div className="accuracy-stats">
            <div className="stats-header">
              <h3>📊 Performance Report</h3>
            </div>
            
            <div className="stats-grid">
              <div className="stat-card correct">
                <div className="stat-icon">✓</div>
                <div className="stat-value">{accuracyStats.correct}</div>
                <div className="stat-label">Correct</div>
              </div>
              
              <div className="stat-card incorrect">
                <div className="stat-icon">✗</div>
                <div className="stat-value">{accuracyStats.incorrect}</div>
                <div className="stat-label">Incorrect</div>
              </div>
              
              <div className="stat-card accuracy">
                <div className="stat-icon">🎯</div>
                <div className="stat-value">{accuracyStats.accuracy_percentage}%</div>
                <div className="stat-label">Accuracy</div>
              </div>
              
              <div className="stat-card total">
                <div className="stat-icon">📈</div>
                <div className="stat-value">{accuracyStats.total_evaluated}</div>
                <div className="stat-label">Total Games</div>
              </div>
            </div>

            <div className="ml-improvements">
              <h4>🔧 Planned ML Improvements</h4>
              <ul>
                <li><strong>Feature Enhancement:</strong> Adding weather conditions, player injuries, and travel distance data to improve prediction accuracy</li>
                <li><strong>Model Upgrades:</strong> Fixing RandomForest and XGBoost version compatibility issues for better ensemble voting</li>
                <li><strong>Data Expansion:</strong> Training on more historical seasons (2020-2024) for improved pattern recognition</li>
                <li><strong>Advanced Features:</strong> Incorporating team momentum, rest days, and head-to-head matchup history</li>
                <li><strong>Hyperparameter Tuning:</strong> Optimizing model parameters using GridSearchCV for each algorithm</li>
                <li><strong>Real-time Updates:</strong> Implementing live odds integration and updating predictions closer to game time</li>
              </ul>
            </div>
          </div>
        )}
        
        <div className="grid">
          {pastPredictions.map((game) => (
            <GameCard key={game.game_id} game={game} mode="past" />
          ))}
        </div>
      </>
    );
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>NFL Prediction Dashboard</h1>
        <p>Visualise the agent\'s ensemble picks, confidence, and how last week played out.</p>
      </header>

      <MetricsPanel metrics={metricsOverview} />

      <div className="tabs" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={tab.id === activeTab ? 'tab active' : 'tab'}
            onClick={() => setActiveTab(tab.id)}
            role="tab"
            aria-selected={tab.id === activeTab}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <section className="content" aria-live="polite">
        <h2>{pageTitle}</h2>
        {renderContent()}
      </section>

      <footer className="disclaimer">
        <div className="disclaimer-content">
          <h3>⚠️ How This Works & Disclaimer</h3>
          <div className="disclaimer-section">
            <h4>🤖 Prediction Methodology</h4>
            <p>
              This application uses <strong>machine learning models</strong> trained on real historical NFL game data collected from ESPN.
              The system analyzes 44+ statistical features including team records, recent performance, spreads, and historical matchups.
              Predictions are generated using an <strong>ensemble approach</strong> combining 6 different ML algorithms:
              LightGBM, Logistic Regression, Gradient Boosting, Neural Network, Random Forest, and XGBoost.
            </p>
          </div>
          <div className="disclaimer-section">
            <h4>📊 Data Sources</h4>
            <p>
              All game data is collected from the <strong>ESPN API</strong>. The models are trained on completed games from previous seasons.
              <strong> This application does NOT make up data</strong> – it learns patterns from real historical outcomes to predict future games.
            </p>
          </div>
          <div className="disclaimer-section warning">
            <h4>⚠️ Important Disclaimers</h4>
            <ul>
              <li><strong>For Educational & Entertainment Purposes Only</strong> – This is a student project demonstrating machine learning concepts.</li>
              <li><strong>No Gambling Advice</strong> – These predictions should NOT be used for betting or wagering of any kind.</li>
              <li><strong>No Accuracy Guarantees</strong> – Sports outcomes are inherently unpredictable. Past model performance does not guarantee future accuracy.</li>
              <li><strong>Use at Your Own Risk</strong> – The developers assume no liability for decisions made based on these predictions.</li>
              <li><strong>Experimental Technology</strong> – Machine learning models can be biased, incorrect, or unreliable.</li>
            </ul>
          </div>
          <div className="disclaimer-footer">
            <p>
              This is a <strong>portfolio/educational project</strong> created for learning purposes. 
              NFL and team names are trademarks of their respective owners. Not affiliated with the NFL or ESPN.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
