import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Sparkles,
  TrendingUp,
  Clock,
  Terminal,
  RefreshCw,
  Loader2
} from 'lucide-react';
import './DashboardPage.css';

export const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/analytics/dashboard', {
        credentials: 'include'
      });
      if (!res.ok) {
        throw new Error('Failed to load dashboard statistics.');
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading-state">
        <Loader2 className="spinning" size={32} />
        <p>Loading analytics & learning insights...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="dashboard-error-state">
        <AlertTriangle size={32} className="error-icon" />
        <p>{error || 'No analytics data available.'}</p>
        <button className="btn-retry" onClick={fetchDashboardData}>
          <RefreshCw size={14} /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard-page-layout">
      <div className="dashboard-header-bar">
        <div>
          <h1>Analytics & Learning Insights</h1>
          <p className="dashboard-subtitle">
            Track your compilation progress, recurring compiler error patterns, and machine-learning diagnostics.
          </p>
        </div>
        <button className="btn-refresh" onClick={fetchDashboardData} title="Refresh data">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* KPI Stats Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon-wrap icon-primary">
            <Layers size={20} />
          </div>
          <div className="kpi-info">
            <span className="kpi-label">Total Submissions</span>
            <span className="kpi-value">{data.total_submissions}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-wrap icon-success">
            <CheckCircle2 size={20} />
          </div>
          <div className="kpi-info">
            <span className="kpi-label">Clean Compiles</span>
            <span className="kpi-value">{data.clean_compiles}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-wrap icon-trending">
            <TrendingUp size={20} />
          </div>
          <div className="kpi-info">
            <span className="kpi-label">Success Rate</span>
            <span className="kpi-value">{data.success_rate}%</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-wrap icon-error">
            <AlertTriangle size={20} />
          </div>
          <div className="kpi-info">
            <span className="kpi-label">Errors Diagnosed</span>
            <span className="kpi-value">{data.total_errors_diagnosed}</span>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-wrap icon-ai">
            <Sparkles size={20} />
          </div>
          <div className="kpi-info">
            <span className="kpi-label">Active ML Model</span>
            <span className="kpi-value model-badge">{data.active_model_version}</span>
          </div>
        </div>
      </div>

      {/* Main Visual Sections */}
      <div className="dashboard-grid-sections">
        {/* Error Frequency by Category */}
        <div className="dashboard-card category-breakdown-card">
          <div className="card-header">
            <div className="header-title">
              <BarChart3 size={18} />
              <h2>Mistakes by Error Category</h2>
            </div>
            <span className="badge-pill">{data.categories_breakdown.length} Categories Encountered</span>
          </div>

          <div className="categories-list">
            {data.categories_breakdown.length === 0 ? (
              <div className="empty-chart-note">
                <CheckCircle2 size={24} />
                <p>No compilation errors recorded yet! Write or analyze code to view breakdown.</p>
              </div>
            ) : (
              data.categories_breakdown.map((item, idx) => (
                <div key={idx} className="category-row">
                  <div className="cat-row-header">
                    <span className="cat-name">{item.category.replace(/_/g, ' ')}</span>
                    <span className="cat-stat">
                      <strong>{item.count}</strong> errors ({item.percentage}%)
                    </span>
                  </div>
                  <div className="cat-bar-track">
                    <div
                      className="cat-bar-fill"
                      style={{ width: `${Math.max(item.percentage, 3)}%` }}
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Mistakes Over Time */}
        <div className="dashboard-card timeline-card">
          <div className="card-header">
            <div className="header-title">
              <Clock size={18} />
              <h2>Activity & Submissions Over Time</h2>
            </div>
          </div>

          <div className="timeline-content">
            {data.mistakes_timeline.length === 0 ? (
              <div className="empty-chart-note">
                <p>No timeline history yet. Start compiling programs in the editor!</p>
              </div>
            ) : (
              <div className="timeline-bars-container">
                {data.mistakes_timeline.map((point, idx) => {
                  const maxSub = Math.max(...data.mistakes_timeline.map(t => t.total_submissions), 1);
                  const cleanHeight = (point.clean_count / maxSub) * 100;
                  const errorHeight = (point.error_count / maxSub) * 100;

                  return (
                    <div key={idx} className="timeline-col" title={`${point.date}: ${point.clean_count} Clean, ${point.error_count} Errors`}>
                      <div className="col-bar-group">
                        <div className="bar-error" style={{ height: `${errorHeight}%` }} />
                        <div className="bar-clean" style={{ height: `${cleanHeight}%` }} />
                      </div>
                      <span className="col-date">{point.date.slice(5)}</span>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="timeline-legend">
              <span className="legend-item"><span className="legend-dot dot-clean" /> Clean Compiles</span>
              <span className="legend-item"><span className="legend-dot dot-error" /> Compiles with Errors</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Mistakes Table */}
      <div className="dashboard-card recent-mistakes-card">
        <div className="card-header">
          <div className="header-title">
            <Terminal size={18} />
            <h2>Recent Compilation Errors & Diagnostic Feedback</h2>
          </div>
        </div>

        <div className="recent-table-wrap">
          {data.recent_mistakes.length === 0 ? (
            <p className="empty-table-note">No recent errors found.</p>
          ) : (
            <table className="recent-mistakes-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Location</th>
                  <th>Compiler Message</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_mistakes.map((m, idx) => (
                  <tr key={idx}>
                    <td>
                      <span className="badge badge-category">
                        {m.category.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td>
                      <span className="line-coord">Line {m.line || '-'}</span>
                    </td>
                    <td className="msg-cell">
                      <code>{m.raw_message}</code>
                    </td>
                    <td className="time-cell">
                      {new Date(m.created_at).toLocaleString([], {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

