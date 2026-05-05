/**
 * Game Analysis Component
 * Shows best moves, blunders, evaluation graph
 */
import React from 'react';
import './Analysis.css';

interface AnalysisProps {
  bestMoves: Array<{ move: string; eval: number }>;
  blunders: Array<{ move: string; eval: number }>;
  mistakes: Array<{ move: string; eval: number }>;
  evaluationGraph: number[];
}

const GameAnalysis: React.FC<AnalysisProps> = ({
  bestMoves,
  blunders,
  mistakes,
  evaluationGraph,
}) => {
  return (
    <div className="game-analysis">
      <h3>Game Analysis</h3>
      
      <div className="analysis-section">
        <h4>📊 Evaluation</h4>
        <div className="evaluation-graph">
          {evaluationGraph.map((evaluation, idx) => (
            <div
              key={idx}
              className={`eval-bar ${evaluation > 0 ? 'white-advantage' : 'black-advantage'}`}
              style={{
                height: `${Math.min(100, Math.abs(evaluation / 10))}%`,
              }}
            />
          ))}
        </div>
      </div>

      <div className="analysis-section">
        <h4>🎯 Best Moves ({bestMoves.length})</h4>
        <div className="move-list-inline">
          {bestMoves.slice(0, 5).map((m, idx) => (
            <span key={idx} className="badge badge-success">{m.move}</span>
          ))}
        </div>
      </div>

      <div className="analysis-section">
        <h4>⚠️ Mistakes ({mistakes.length})</h4>
        <div className="move-list-inline">
          {mistakes.slice(0, 5).map((m, idx) => (
            <span key={idx} className="badge badge-warning">{m.move}</span>
          ))}
        </div>
      </div>

      <div className="analysis-section">
        <h4>❌ Blunders ({blunders.length})</h4>
        <div className="move-list-inline">
          {blunders.slice(0, 5).map((m, idx) => (
            <span key={idx} className="badge badge-danger">{m.move}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GameAnalysis;
