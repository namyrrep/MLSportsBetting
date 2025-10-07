import { useEffect, useState } from 'react';
import axios from 'axios';
import './ModelsPage.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const formatDate = (isoDate) => {
  if (!isoDate) return 'N/A';
  const parsed = new Date(isoDate);
  if (Number.isNaN(parsed.getTime())) return isoDate;
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
  }).format(parsed);
};

const formatPercent = (value) => {
  if (value === null || value === undefined) return '—';
  return `${(value * 100).toFixed(1)}%`;
};

const formatDuration = (seconds) => {
  if (!seconds) return '—';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}m ${secs}s`;
};

function ModelCard({ model, onClick }) {
  const accuracyClass = (acc) => {
    if (acc >= 0.7) return 'high';
    if (acc >= 0.55) return 'medium';
    return 'low';
  };

  return (
    <div className="model-card" onClick={() => onClick(model)}>
      <div className="model-header">
        <h3>{model.model_name}</h3>
        {model.is_active ? (
          <span className="status-badge active">Active</span>
        ) : (
          <span className="status-badge inactive">Inactive</span>
        )}
      </div>

      <div className="model-stat-row">
        <div className={`model-accuracy ${accuracyClass(model.current_accuracy)}`}>
          <span className="stat-value">{formatPercent(model.current_accuracy)}</span>
          <span className="stat-label">Current Accuracy</span>
        </div>
        <div className="model-stat">
          <span className="stat-value">{formatPercent(model.best_accuracy)}</span>
          <span className="stat-label">Best Accuracy</span>
        </div>
      </div>

      <div className="model-meta">
        <div className="meta-item">
          <span className="meta-icon">🔄</span>
          <span className="meta-text">{model.total_training_count || 0} trainings</span>
        </div>
        <div className="meta-item">
          <span className="meta-icon">📅</span>
          <span className="meta-text">Last: {formatDate(model.last_trained_date)}</span>
        </div>
      </div>

      <div className="model-version">
        <span>v{model.current_version || '1.0'}</span>
      </div>
    </div>
  );
}

function PerformanceTrendChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="no-data">No training history available</div>;
  }

  const maxAccuracy = Math.max(...data.map(d => d.test_accuracy || 0));
  const minAccuracy = Math.min(...data.map(d => d.test_accuracy || 0));
  const range = maxAccuracy - minAccuracy || 0.5;

  return (
    <div className="performance-chart">
      <h4>📈 Training Performance Over Time</h4>
      <svg className="chart-svg" viewBox="0 0 600 180" preserveAspectRatio="none">
        <defs>
          <linearGradient id="perfGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#8b5cf6" />
            <stop offset="100%" stopColor="#ec4899" />
          </linearGradient>
          <linearGradient id="perfAreaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(139, 92, 246, 0.3)" />
            <stop offset="100%" stopColor="rgba(139, 92, 246, 0.05)" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        <line x1="0" y1="45" x2="600" y2="45" stroke="rgba(148, 163, 184, 0.1)" strokeWidth="1" />
        <line x1="0" y1="90" x2="600" y2="90" stroke="rgba(148, 163, 184, 0.15)" strokeWidth="1" />
        <line x1="0" y1="135" x2="600" y2="135" stroke="rgba(148, 163, 184, 0.1)" strokeWidth="1" />

        {/* Area fill */}
        <path
          d={`M 0 180 ${data.map((d, i) => {
            const x = (i / (data.length - 1 || 1)) * 600;
            const y = 180 - ((d.test_accuracy - minAccuracy + 0.05) / (range + 0.1)) * 160;
            return `L ${x} ${y}`;
          }).join(' ')} L 600 180 Z`}
          fill="url(#perfAreaGradient)"
        />

        {/* Line */}
        <path
          d={data.map((d, i) => {
            const x = (i / (data.length - 1 || 1)) * 600;
            const y = 180 - ((d.test_accuracy - minAccuracy + 0.05) / (range + 0.1)) * 160;
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
          }).join(' ')}
          fill="none"
          stroke="url(#perfGradient)"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {data.map((d, i) => {
          const x = (i / (data.length - 1 || 1)) * 600;
          const y = 180 - ((d.test_accuracy - minAccuracy + 0.05) / (range + 0.1)) * 160;
          return (
            <g key={i}>
              <circle cx={x} cy={y} r="4" fill="#8b5cf6" stroke="#1e293b" strokeWidth="2" />
              <title>{formatPercent(d.test_accuracy)}</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function TrainingHistoryTable({ sessions }) {
  if (!sessions || sessions.length === 0) {
    return <div className="no-data">No training sessions recorded</div>;
  }

  return (
    <div className="training-history">
      <h4>🗂️ Training History</h4>
      <div className="history-table-container">
        <table className="history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Training Samples</th>
              <th>Test Accuracy</th>
              <th>F1 Score</th>
              <th>ROC AUC</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session, idx) => (
              <tr key={idx}>
                <td>{formatDate(session.training_date)}</td>
                <td>{session.training_samples || '—'}</td>
                <td className="accuracy-cell">{formatPercent(session.test_accuracy)}</td>
                <td>{formatPercent(session.f1_score)}</td>
                <td>{formatPercent(session.roc_auc)}</td>
                <td>{formatDuration(session.training_duration_seconds)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ModelDetailModal({ model, onClose }) {
  const [modelData, setModelData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModelDetails = async () => {
      try {
        const [historyResponse, statsResponse] = await Promise.all([
          axios.get(`${API_BASE_URL}/models/${model.model_name}/history`),
          axios.get(`${API_BASE_URL}/models/${model.model_name}/stats`),
        ]);

        setModelData({
          history: historyResponse.data,
          stats: statsResponse.data,
        });
      } catch (err) {
        console.error('Failed to load model details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchModelDetails();
  }, [model.model_name]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        
        <div className="modal-header">
          <h2>{model.model_name}</h2>
          <span className="model-version-badge">v{model.current_version || '1.0'}</span>
        </div>

        {loading ? (
          <div className="modal-loading">Loading details...</div>
        ) : modelData ? (
          <>
            <div className="model-stats-grid">
              <div className="stat-box">
                <span className="stat-icon">🎯</span>
                <div>
                  <div className="stat-number">{formatPercent(modelData.stats.statistics.current_accuracy)}</div>
                  <div className="stat-title">Current Accuracy</div>
                </div>
              </div>
              <div className="stat-box">
                <span className="stat-icon">⏱️</span>
                <div>
                  <div className="stat-number">{formatDuration(modelData.stats.statistics.avg_training_time_seconds)}</div>
                  <div className="stat-title">Avg Training Time</div>
                </div>
              </div>
              <div className="stat-box">
                <span className="stat-icon">🔄</span>
                <div>
                  <div className="stat-number">{modelData.stats.metadata.total_training_count}</div>
                  <div className="stat-title">Total Trainings</div>
                </div>
              </div>
              <div className="stat-box">
                <span className="stat-icon">📊</span>
                <div>
                  <div className="stat-number">{formatPercent(modelData.stats.metadata.best_accuracy)}</div>
                  <div className="stat-title">Best Accuracy</div>
                </div>
              </div>
            </div>

            <PerformanceTrendChart data={modelData.history.performance_trend} />
            <TrainingHistoryTable sessions={modelData.history.training_sessions} />
          </>
        ) : (
          <div className="modal-error">Failed to load model details</div>
        )}
      </div>
    </div>
  );
}

export default function ModelsPage() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/models/overview`);
        setModels(response.data.models || []);
      } catch (err) {
        setError(err.message || 'Failed to load models');
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, []);

  if (loading) {
    return (
      <div className="models-page">
        <div className="page-header">
          <h1>🤖 Model Analytics</h1>
        </div>
        <div className="loading-message">Loading models...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="models-page">
        <div className="page-header">
          <h1>🤖 Model Analytics</h1>
        </div>
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="models-page">
      <div className="page-header">
        <h1>🤖 Model Analytics</h1>
        <p>Track individual model performance, training history, and efficiency metrics</p>
      </div>

      <div className="models-summary">
        <div className="summary-card">
          <span className="summary-icon">🎯</span>
          <div>
            <div className="summary-value">{models.length}</div>
            <div className="summary-label">Active Models</div>
          </div>
        </div>
        <div className="summary-card">
          <span className="summary-icon">🔄</span>
          <div>
            <div className="summary-value">
              {models.reduce((sum, m) => sum + (m.total_training_count || 0), 0)}
            </div>
            <div className="summary-label">Total Trainings</div>
          </div>
        </div>
        <div className="summary-card">
          <span className="summary-icon">📈</span>
          <div>
            <div className="summary-value">
              {formatPercent(
                models.reduce((sum, m) => sum + (m.current_accuracy || 0), 0) / (models.length || 1)
              )}
            </div>
            <div className="summary-label">Avg Accuracy</div>
          </div>
        </div>
      </div>

      <div className="models-grid">
        {models.map((model) => (
          <ModelCard key={model.model_name} model={model} onClick={setSelectedModel} />
        ))}
      </div>

      {selectedModel && (
        <ModelDetailModal model={selectedModel} onClose={() => setSelectedModel(null)} />
      )}
    </div>
  );
}
