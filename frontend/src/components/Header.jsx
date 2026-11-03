import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, Terminal, User as UserIcon, LogOut, Settings as SettingsIcon, BarChart2 } from 'lucide-react';
import './Header.css';

export const Header = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  return (
    <header className="app-header">
      <div className="header-container">
        <Link to="/" className="brand-logo">
          <span className="brand-icon">
            <Terminal size={18} strokeWidth={2.2} />
          </span>
          <div className="brand-text">
            <span className="brand-title">C++ Error Tutor</span>
            <span className="brand-version">v1.0</span>
          </div>
        </Link>

        {user && (
          <nav className="header-nav">
            <Link
              to="/editor"
              className={`nav-link ${location.pathname === '/editor' || location.pathname === '/' ? 'active' : ''}`}
            >
              Editor
            </Link>
            <Link
              to="/history"
              className={`nav-link ${location.pathname === '/history' ? 'active' : ''}`}
            >
              History
            </Link>
            <Link
              to="/dashboard"
              className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
            >
              Dashboard
            </Link>
          </nav>
        )}

        <div className="header-actions">
          <button
            onClick={toggleTheme}
            className="theme-toggle-btn"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </button>

          {user ? (
            <div className="user-profile">
              <Link to="/settings" className="user-email user-settings-link" title="Account Settings & Privacy">
                <UserIcon size={14} className="user-icon" />
                <span>{user.name || user.email.split('@')[0]}</span>
                <SettingsIcon size={13} style={{ marginLeft: '4px', opacity: 0.7 }} />
              </Link>
              <button onClick={logout} className="btn-logout" title="Sign out">
                <LogOut size={15} />
                <span>Sign out</span>
              </button>
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login" className="btn btn-outline" style={{ padding: '6px 14px' }}>
                Sign in
              </Link>
              <Link to="/register" className="btn btn-primary" style={{ padding: '6px 14px' }}>
                Create account
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
