/**
 * Game Timer Component
 * Displays countdown timer for each player
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './GameTimer.css';

interface GameTimerProps {
  whiteTime: number; // milliseconds
  blackTime: number;
  isWhiteTurn: boolean;
  isActive: boolean;
  onTimeExpired?: (color: 'white' | 'black') => void;
}

const formatTime = (ms: number): string => {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds
      .toString()
      .padStart(2, '0')}`;
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};

const GameTimer: React.FC<GameTimerProps> = ({
  whiteTime,
  blackTime,
  isWhiteTurn,
  isActive,
  onTimeExpired,
}) => {
  const [displayWhiteTime, setDisplayWhiteTime] = useState(whiteTime);
  const [displayBlackTime, setDisplayBlackTime] = useState(blackTime);

  useEffect(() => {
    setDisplayWhiteTime(whiteTime);
    setDisplayBlackTime(blackTime);
  }, [whiteTime, blackTime]);

  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      if (isWhiteTurn) {
        setDisplayWhiteTime((prev) => {
          const newTime = Math.max(0, prev - 100);
          if (newTime === 0 && onTimeExpired) {
            onTimeExpired('white');
          }
          return newTime;
        });
      } else {
        setDisplayBlackTime((prev) => {
          const newTime = Math.max(0, prev - 100);
          if (newTime === 0 && onTimeExpired) {
            onTimeExpired('black');
          }
          return newTime;
        });
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isActive, isWhiteTurn, onTimeExpired]);

  const getTimerClass = (isWhite: boolean) => {
    const time = isWhite ? displayWhiteTime : displayBlackTime;
    if (time > 600000) return 'plenty';
    if (time > 60000) return 'normal';
    if (time > 10000) return 'warning';
    return 'critical';
  };

  const getTimerVariants = (isWhite: boolean) => ({
    active: isWhite === isWhiteTurn ? { scale: 1.05 } : {},
  });

  return (
    <div className="game-timer">
      <motion.div
        className={`timer ${getTimerClass(false)} ${!isWhiteTurn ? 'active' : ''}`}
        animate={getTimerVariants(false)}
      >
        <div className="timer-label">Black</div>
        <div className="timer-value">{formatTime(displayBlackTime)}</div>
      </motion.div>

      <motion.div
        className={`timer ${getTimerClass(true)} ${isWhiteTurn ? 'active' : ''}`}
        animate={getTimerVariants(true)}
      >
        <div className="timer-label">White</div>
        <div className="timer-value">{formatTime(displayWhiteTime)}</div>
      </motion.div>
    </div>
  );
};

export default GameTimer;
