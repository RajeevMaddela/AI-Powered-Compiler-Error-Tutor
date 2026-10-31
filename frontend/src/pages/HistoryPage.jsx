import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Trash2,
  Code2,
  ChevronRight,
  Loader2,
  Inbox,
  ArrowLeft,
  Terminal
} from 'lucide-react';
import './HistoryPage.css';

export const HistoryPage = () => {
  const [submissions, setSubmissions] = useState([]);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await fetch('/api/history', { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to load history');
      const data = await res.json();
      setSubmissions(data);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSubmission = async (id) => {
    setDetailLoading(true);
    try {
      const res = await fetch(`/api/history/${id}`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to load submission details');
      const data = await res.json();
      setSelectedSubmission(data);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDeleteSubmission = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this submission record?')) return;

    try {
      const res = await fetch(`/api/history/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to delete submission');

      setSubmissions(prev => prev.filter(s => s.id !== id));
      if (selectedSubmission && selectedSubmission.id === id) {
        setSelectedSubmission(null);
      }
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  const handleClearAllHistory = async () => {
    if (!window.confirm('Are you sure you want to delete ALL your submission history? This cannot be undone.')) return;

    try {
      const res = await fetch('/api/history', {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to clear history');

      setSubmissions([]);
      setSelectedSubmission(null);
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  return (
    <div className="history-page-layout">
      <div className="history-header-bar">
        <div className="history-title-group">
          <h1>Submission History</h1>
          <p className="history-subtitle">
            Review your past C++ compilations and diagnosed errors.
          </p>
        </div>

        {submissions.length > 0 && (
          <button
            onClick={handleClearAllHistory}
            className="btn btn-outline btn-clear-all"
            title="Delete all submission history"
          >
            <Trash2 size={14} />
            <span>Clear All History</span>
          </button>
        )}
      </div>

      {errorMsg && (
        <div className="alert alert-error" style={{ margin: '0 24px 16px' }}>
          <AlertTriangle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {loading ? (
        <div className="history-loading-state">
          <Loader2 className="spin" size={24} />
          <span>Loading past submissions...</span>
        </div>
      ) : submissions.length === 0 ? (
        <div className="history-empty-state">
          <Inbox size={42} className="empty-icon" />
          <h2>No Submissions Yet</h2>
          <p>
            When you compile C++ code in the Editor, your analysis runs will appear here for review.
          </p>
          <Link to="/editor" className="btn btn-primary" style={{ marginTop: '12px' }}>
            Go to Editor
          </Link>
        </div>
      ) : (
        <div className="history-split-view">
          {/* Left Column: Submissions List */}
          <div className="history-list-pane">
            {submissions.map((sub) => {
              const isSelected = selectedSubmission && selectedSubmission.id === sub.id;
              const isClean = sub.compile_status === 'clean';

              return (
                <div
                  key={sub.id}
                  className={`history-item-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSelectSubmission(sub.id)}
                >
                  <div className="history-item-top">
                    <div className="status-indicator">
                      {isClean ? (
                        <span className="badge badge-success">Clean</span>
                      ) : sub.compile_status === 'timeout' ? (
                        <span className="badge badge-warning">Timeout</span>
                      ) : (
                        <span className="badge badge-error">
                          {sub.error_count} {sub.error_count === 1 ? 'Error' : 'Errors'}
                        </span>
                      )}
                      <span className="history-duration">{sub.duration_ms} ms</span>
                    </div>

                    <button
                      onClick={(e) => handleDeleteSubmission(e, sub.id)}
                      className="btn-item-delete"
                      title="Delete record"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>

                  <div className="history-item-date">
                    <Clock size={12} />
                    <span>{new Date(sub.created_at).toLocaleString()}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Detailed View */}
          <div className="history-detail-pane">
            {detailLoading ? (
              <div className="history-loading-state">
                <Loader2 className="spin" size={20} />
                <span>Loading submission code and diagnostics...</span>
              </div>
            ) : selectedSubmission ? (
              <div className="detail-container">
                <div className="detail-meta-bar">
                  <div>
                    <h3 className="detail-title">Submission #{selectedSubmission.id}</h3>
                    <span className="detail-timestamp">
                      {new Date(selectedSubmission.created_at).toLocaleString()} ({selectedSubmission.duration_ms} ms)
                    </span>
                  </div>
                  <span className={`badge ${selectedSubmission.compile_status === 'clean' ? 'badge-success' : 'badge-error'}`}>
                    {selectedSubmission.compile_status.toUpperCase()}
                  </span>
                </div>

                <div className="detail-code-section">
                  <div className="detail-section-label">
                    <Code2 size={14} /> Source Code
                  </div>
                  <pre className="code-viewer">
                    <code>{selectedSubmission.code}</code>
                  </pre>
                </div>

                <div className="detail-diagnostics-section">
                  <div className="detail-section-label">
                    <Terminal size={14} /> Diagnostic Errors ({selectedSubmission.errors.length})
                  </div>

                  {selectedSubmission.errors.length === 0 ? (
                    <div className="clean-compilation-notice">
                      <CheckCircle2 size={18} />
                      <span>This program compiled cleanly with 0 errors.</span>
                    </div>
                  ) : (
                    <div className="detail-errors-list">
                      {selectedSubmission.errors.map((err, idx) => (
                        <div key={idx} className="diagnostic-card card-error">
                          <div className="card-top-meta">
                            <span className="badge badge-error">
                              {err.severity.toUpperCase()}
                            </span>
                            {err.line && (
                              <span className="line-coord-badge">
                                Line {err.line}{err.column ? `:${err.column}` : ''}
                              </span>
                            )}
                          </div>
                          <div className="card-message">
                            <code>{err.message}</code>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="detail-placeholder">
                <ChevronRight size={32} className="empty-icon" />
                <p>Select a submission on the left to inspect its source code and diagnosed errors.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
