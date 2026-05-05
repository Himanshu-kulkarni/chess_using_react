/**
 * Player Stats Component
 * Shows player rating and statistics
 */
import React from 'react';
import './PlayerStats.css';

interface PlayerStatsProps {
  username: string;
  standardRating: number;
  blitzRating: number;
  rapidRating: number;
  wins: number;
  losses: number;
  draws: number;
}

const getRatingTitle = (rating: number): string => {
  if (rating < 1000) return 'Beginner';
  if (rating < 1400) return 'Intermediate';
  if (rating < 1700) return 'Advanced';
  if (rating < 2000) return 'Expert';
  if (rating < 2200) return 'Master';
  return 'Grandmaster';
};

const PlayerStats: React.FC<PlayerStatsProps> = ({
  username,
  standardRating,
  blitzRating,
  rapidRating,
  wins,
  losses,
  draws,
}) => {
  const totalGames = wins + losses + draws;
  const winRate = totalGames > 0 ? (wins / totalGames * 100).toFixed(1) : '0';

  return (
    <div className="player-stats">
      <div className="player-header">
        <h2>{username}</h2>
        <span className="rating-badge">{standardRating}</span>
      </div>

      <div className="rating-title">{getRatingTitle(standardRating)}</div>

      <div className="ratings-grid">
        <div className="rating-card">
          <div className="rating-type">Standard</div>
          <div className="rating-value">{standardRating}</div>
        </div>
        <div className="rating-card">
          <div className="rating-type">Rapid</div>
          <div className="rating-value">{rapidRating}</div>
        </div>
        <div className="rating-card">
          <div className="rating-type">Blitz</div>
          <div className="rating-value">{blitzRating}</div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-value wins">{wins}</div>
          <div className="stat-label">Wins</div>
        </div>
        <div className="stat-item">
          <div className="stat-value draws">{draws}</div>
          <div className="stat-label">Draws</div>
        </div>
        <div className="stat-item">
          <div className="stat-value losses">{losses}</div>
          <div className="stat-label">Losses</div>
        </div>
        <div className="stat-item">
          <div className="stat-value total">{totalGames}</div>
          <div className="stat-label">Games</div>
        </div>
      </div>

      <div className="win-rate">
        <div className="win-rate-label">Win Rate</div>
        <div className="win-rate-value">{winRate}%</div>
        <div className="win-rate-bar">
          <div
            className="win-rate-fill"
            style={{ width: `${winRate}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default PlayerStats;
