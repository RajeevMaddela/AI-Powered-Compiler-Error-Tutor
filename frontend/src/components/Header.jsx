import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, Terminal, User as UserIcon, LogOut } from 'lucide-react';
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
              <span className="user-email" title={user.email}>
                <UserIcon size={14} className="user-icon" />
                {user.name || user.email.split('@')[0]}
              </span>
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
