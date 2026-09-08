import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './App.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ORCA Application Crash:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          height: '100vh',
          width: '100vw',
          backgroundColor: '#0a1628',
          color: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: "'Inter', -apple-system, sans-serif",
          padding: '2rem',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>🐋</div>
          <h2 style={{ color: '#00d4ff', marginBottom: '0.75rem', fontSize: '1.5rem' }}>ORCA Marine Intelligence Interface</h2>
          <p style={{ color: '#94a3b8', maxWidth: '580px', marginBottom: '1.5rem', lineHeight: 1.6, fontSize: '0.95rem' }}>
            A client-side initialization anomaly occurred in the browser session. Click below to reload the collaborative marine agent workspace.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: 'linear-gradient(90deg, #00d4ff, #0066ff)',
              color: 'white',
              border: 'none',
              padding: '0.85rem 2.2rem',
              borderRadius: '50px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '1rem',
              boxShadow: '0 4px 20px rgba(0, 212, 255, 0.4)'
            }}
            type="button"
          >
            🔄 Reload Workspace
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
