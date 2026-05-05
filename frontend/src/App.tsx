/**
 * Main App Component
 * Sets up routing and layout
 */
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import GamePage from './pages/Game';
import './styles/App.css';

const HomePage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handlePlayVsAI = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/games/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          white_player: 'Human',
          black_player: 'AI',
          time_control: 'rapid',
          ai_difficulty: 'medium',
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create game');
      }
      
      const game = await response.json();
      navigate(`/game/${game.game_id}`);
    } catch (error) {
      console.error('Error creating game:', error);
      alert('Failed to create game. Make sure the backend is running on localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      <div className="hero">
        <h1>♟️ Chess Platform</h1>
        <p>Play chess online with real-time multiplayer and advanced AI</p>
        
        <div className="action-buttons">
          <button onClick={handlePlayVsAI} className="btn btn-primary btn-large" disabled={loading}>
            {loading ? 'Starting...' : 'Play vs AI'}
          </button>
          <Link to="/multiplayer" className="btn btn-secondary btn-large">
            Play Online
          </Link>
        </div>
      </div>

      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🤖</div>
          <h3>Advanced AI Engine</h3>
          <p>Iterative deepening with transposition tables & quiescence search</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🌐</div>
          <h3>Real-time Multiplayer</h3>
          <p>Play against friends with WebSocket synchronization</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h3>ELO Ratings</h3>
          <p>Track your rating across different time controls</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📈</div>
          <h3>Game Analysis</h3>
          <p>Get instant analysis with best moves and blunders</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">⏱️</div>
          <h3>Multiple Time Controls</h3>
          <p>Blitz, Rapid, and Classical formats</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🎮</div>
          <h3>Smooth Gameplay</h3>
          <p>Drag-and-drop interface with move animations</p>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <Link to="/" className="navbar-brand">
            ♟️ Chess
          </Link>
          <div className="navbar-links">
            <Link to="/">Home</Link>
            <Link to="/multiplayer">Multiplayer</Link>
            <Link to="/profile">Profile</Link>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/game/:gameId" element={<GamePage />} />
            <Route path="/multiplayer" element={<div>Multiplayer (Coming Soon)</div>} />
            <Route path="/profile" element={<div>Profile (Coming Soon)</div>} />
          </Routes>
        </main>

        <footer className="footer">
          <p>&copy; 2024 Chess Platform. All rights reserved.</p>
          <p>Built with React, FastAPI, and ♟️ Chess Engine</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
