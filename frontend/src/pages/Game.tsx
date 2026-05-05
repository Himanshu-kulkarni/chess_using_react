/**
 * Main Game Page
 * Displays active game with board, timers, and move history
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  Board,
  GameTimer,
  MoveList,
  GameAnalysis,
  PlayerStats,
} from '../components';
import '../styles/Game.css';

interface GameData {
  game_id: string;
  white_player: string;
  black_player: string;
  fen: string;
  moves: string[];
  white_time: number;
  black_time: number;
  is_finished: boolean;
  result: string | null;
  current_turn: 'white' | 'black';
}

const GamePage: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const [game, setGame] = useState<GameData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMoveIndex, setSelectedMoveIndex] = useState<number | null>(null);

  // Fetch game data
  useEffect(() => {
    const fetchGame = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/games/${gameId}`);
        if (!response.ok) throw new Error('Failed to fetch game');
        const data = await response.json();
        setGame(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchGame();
    const interval = setInterval(fetchGame, 1000);
    return () => clearInterval(interval);
  }, [gameId]);

  // Handle move
  const handleMove = useCallback(
    async (from: string, to: string) => {
      if (!game || game.is_finished) return;

      try {
        const response = await fetch(`http://localhost:8000/api/games/${gameId}/move`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            from_square: from,
            to_square: to,
            player: game.current_turn === 'white' ? game.white_player : game.black_player,
          }),
        });

        if (!response.ok) throw new Error('Invalid move');
        const updated = await response.json();
        setGame(updated);
      } catch (err) {
        console.error('Move error:', err);
      }
    },
    [game, gameId]
  );

  // Handle resign
  const handleResign = async () => {
    if (!game) return;
    const playerColor = game.current_turn === 'white' ? game.white_player : game.black_player;
    try {
      const response = await fetch(
        `http://localhost:8000/api/games/${gameId}/resign?player=${playerColor}`,
        { method: 'POST' }
      );
      const updated = await response.json();
      setGame(updated);
    } catch (err) {
      console.error('Resign error:', err);
    }
  };

  if (loading) return <div className="loading">Loading game...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!game) return <div className="error">Game not found</div>;

  const legalMoves = []; // Would need to fetch from backend

  return (
    <div className="game-page">
      <div className="game-header">
        <h1>Chess Game</h1>
        <div className="player-info">
          <div className={`player ${game.current_turn === 'white' ? 'active' : ''}`}>
            {game.white_player} (White)
          </div>
          <span className="vs">vs</span>
          <div className={`player ${game.current_turn === 'black' ? 'active' : ''}`}>
            {game.black_player} (Black)
          </div>
        </div>
      </div>

      <div className="game-container">
        <div className="game-main">
          <GameTimer
            whiteTime={game.white_time}
            blackTime={game.black_time}
            isWhiteTurn={game.current_turn === 'white'}
            isActive={!game.is_finished}
          />

          <Board
            fen={game.fen}
            legalMoves={legalMoves}
            onMove={handleMove}
            disabled={game.is_finished}
            perspective="white"
          />

          <div className="game-controls">
            <button className="btn btn-secondary" onClick={handleResign}>
              Resign
            </button>
            <button className="btn btn-secondary">Offer Draw</button>
            <button className="btn btn-secondary">Undo</button>
          </div>
        </div>

        <div className="game-sidebar">
          <MoveList
            moves={game.moves}
            selectedMoveIndex={selectedMoveIndex}
            onMoveClick={setSelectedMoveIndex}
          />
        </div>
      </div>

      {game.is_finished && (
        <div className="game-result">
          <h2>
            {game.result === 'white_win'
              ? '♔ White Wins'
              : game.result === 'black_win'
              ? '♚ Black Wins'
              : '½–½ Draw'}
          </h2>
          <button className="btn btn-primary">View Analysis</button>
          <button className="btn btn-secondary">Play Again</button>
        </div>
      )}
    </div>
  );
};

export default GamePage;
