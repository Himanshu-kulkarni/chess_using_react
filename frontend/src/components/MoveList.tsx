/**
 * Move List Component
 * Displays game moves in chess notation
 */
import React from 'react';
import './MoveList.css';

interface MoveListProps {
  moves: string[];
  onMoveClick?: (moveIndex: number) => void;
  selectedMoveIndex?: number;
}

const MoveList: React.FC<MoveListProps> = ({
  moves,
  onMoveClick,
  selectedMoveIndex,
}) => {
  return (
    <div className="move-list">
      <div className="move-list-header">
        <h3>Move History</h3>
      </div>
      <div className="move-list-content">
        {moves.length === 0 ? (
          <p className="no-moves">No moves yet</p>
        ) : (
          <div className="moves-grid">
            {moves.map((move, idx) => (
              <div
                key={idx}
                className={`move-item ${
                  idx === selectedMoveIndex ? 'selected' : ''
                }`}
                onClick={() => onMoveClick?.(idx)}
              >
                {idx % 2 === 0 && (
                  <span className="move-number">{Math.floor(idx / 2) + 1}.</span>
                )}
                <span className="move-notation">{move}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MoveList;
