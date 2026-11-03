import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  User,
  Shield,
  Trash2,
  Cpu,
  AlertCircle,
  CheckCircle2,
  Lock,
  Loader2,
  RotateCcw
} from 'lucide-react';
import './SettingsPage.css';

export const SettingsPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [consentDecision, setConsentDecision] = useState('denied');
  const [loading, setLoading] = useState(true);
  const [updatingConsent, setUpdatingConsent] = useState(false);
  const [msg, setMsg] = useState({ text: '', type: '' });

  const fetchProfileAndConsent = async () => {
    setLoading(true);
    try {
      const [profRes, consRes] = await Promise.all([
        fetch('/api/account/profile', { credentials: 'include' }),
        fetch('/api/consent', { credentials: 'include' })
      ]);

      if (profRes.ok) {
        const profData = await profRes.json();
        setProfile(profData);
      }
      if (consRes.ok) {
        const consData = await consRes.json();
        setConsentDecision(consData.decision || 'denied');
      }
    } catch (err) {
      setMsg({ text: 'Failed to load profile details.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfileAndConsent();
  }, []);

  const handleConsentToggle = async (newDecision) => {
    setUpdatingConsent(true);
    setMsg({ text: '', type: '' });
    try {
      const res = await fetch('/api/consent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ decision: newDecision })
      });

      if (!res.ok) throw new Error('Failed to update consent decision');
      const data = await res.json();
      setConsentDecision(data.decision);
      setMsg({
        text: `Consent preference successfully updated to '${data.decision}'.`,
        type: 'success'
      });
    } catch (err) {
      setMsg({ text: err.message, type: 'error' });
    } finally {
      setUpdatingConsent(false);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Are you sure you want to delete all your past submission history? This cannot be undone.')) {
      return;
    }

    try {
      const res = await fetch('/api/account/clear-history', {
        method: 'POST',
        credentials: 'include'
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to clear history');

      setMsg({ text: data.message, type: 'success' });
      fetchProfileAndConsent();
    } catch (err) {
      setMsg({ text: err.message, type: 'error' });
    }
  };

  const handleDeleteAccount = async () => {
    const confirmation = window.prompt(
      'DANGER: To confirm permanently deleting your account and all associated submissions and feedback, type DELETE below:'
    );
    if (confirmation !== 'DELETE') return;

    try {
      const res = await fetch('/api/account', {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to delete account');

      logout();
      navigate('/login');
    } catch (err) {
      setMsg({ text: err.message, type: 'error' });
    }
  };

  if (loading) {
    return (
      <div className="settings-loading-state">
        <Loader2 className="spinning" size={32} />
        <p>Loading account settings...</p>
      </div>
    );
  }

  return (
    <div className="settings-page-layout">
      <div className="settings-header">
        <h1>Settings & Privacy</h1>
        <p className="settings-subtitle">
          Manage your account profile, machine-learning retraining consent, and data preferences.
        </p>
      </div>

      {msg.text && (
        <div className={`settings-alert ${msg.type === 'success' ? 'alert-success' : 'alert-error'}`}>
          {msg.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          <span>{msg.text}</span>
        </div>
      )}

      <div className="settings-sections-list">
        {/* Profile Card */}
        <div className="settings-card">
          <div className="card-title-group">
            <User size={18} className="title-icon" />
            <div>
              <h2>Account Information</h2>
              <p>Your authentication details and account statistics.</p>
            </div>
          </div>

          <div className="card-fields-grid">
            <div className="field-item">
              <span className="field-label">Name</span>
              <span className="field-value">{profile?.name || 'Student'}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Email</span>
              <span className="field-value">{profile?.email}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Role</span>
              <span className="field-value badge-role">{profile?.role || 'student'}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Total Submissions</span>
              <span className="field-value">{profile?.total_submissions || 0}</span>
            </div>
          </div>
        </div>

        {/* Model Information */}
        <div className="settings-card">
          <div className="card-title-group">
            <Cpu size={18} className="title-icon" />
            <div>
              <h2>Machine Learning Engine</h2>
              <p>Active model parameters and compiler diagnostic configuration.</p>
            </div>
          </div>

          <div className="card-fields-grid">
            <div className="field-item">
              <span className="field-label">Active Model Version</span>
              <span className="field-value font-mono">{profile?.active_model_version || 'v1.1.0'}</span>
            </div>
            <div className="field-item">
              <span className="field-label">Calibration Threshold</span>
              <span className="field-value font-mono">0.55 (Abstain Safe)</span>
            </div>
            <div className="field-item">
              <span className="field-label">Compiler Pipeline</span>
              <span className="field-value font-mono">GCC 13 (C++17 Sandbox)</span>
            </div>
            <div className="field-item">
              <span className="field-label">Privacy Guarantee</span>
              <span className="field-value badge-privacy">AST Sanitized (Zero Code Retention)</span>
            </div>
          </div>
        </div>

        {/* Retraining Consent Flow (M3.4) */}
        <div className="settings-card consent-card">
          <div className="card-title-group">
            <Shield size={18} className="title-icon icon-shield" />
            <div>
              <h2>Retraining Consent Preference</h2>
              <p>Control whether your error diagnostics help improve the AI compiler tutor.</p>
            </div>
          </div>

          <div className="consent-explainer">
            <p>
              When consent is <strong>granted</strong>, anonymized compiler diagnostic messages and your category feedback
              (e.g., "Not helpful $\rightarrow$ Missing Return") are securely included in audited model retraining rounds.
            </p>
            <p className="privacy-highlight">
              <Lock size={14} /> <strong>Strict Privacy:</strong> Student code, variable names, and function identifiers
              are always replaced with <code>&lt;ID&gt;</code> by the privacy sanitizer before any training vector is constructed.
              By default, your consent is <strong>denied</strong>.
            </p>
          </div>

          <div className="consent-action-row">
            <div className="status-indicator">
              <span>Current Status:</span>
              <span className={`badge ${consentDecision === 'granted' ? 'badge-consent-granted' : 'badge-consent-denied'}`}>
                {consentDecision.toUpperCase()}
              </span>
            </div>

            <div className="consent-buttons">
              {consentDecision === 'granted' ? (
                <button
                  className="btn-revoke-consent"
                  onClick={() => handleConsentToggle('denied')}
                  disabled={updatingConsent}
                >
                  Revoke Consent (Opt-Out)
                </button>
              ) : (
                <button
                  className="btn-grant-consent"
                  onClick={() => handleConsentToggle('granted')}
                  disabled={updatingConsent}
                >
                  Grant Retraining Consent (Opt-In)
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="settings-card danger-zone-card">
          <div className="card-title-group">
            <Trash2 size={18} className="title-icon icon-danger" />
            <div>
              <h2>Danger Zone</h2>
              <p>Irreversible data management actions.</p>
            </div>
          </div>

          <div className="danger-actions-list">
            <div className="danger-action-row">
              <div>
                <h4>Clear Compilation History</h4>
                <p>Delete all your past C++ code submissions and compiler diagnostics.</p>
              </div>
              <button className="btn-danger-outline" onClick={handleClearHistory}>
                Clear History
              </button>
            </div>

            <div className="danger-action-row">
              <div>
                <h4>Delete Account Permanently</h4>
                <p>Permanently remove your account, profile, all history, and feedback records.</p>
              </div>
              <button className="btn-danger-solid" onClick={handleDeleteAccount}>
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

