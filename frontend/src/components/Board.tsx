/**
 * Main Chess Board Component
 * Handles piece rendering, drag-and-drop, highlighting
 */
import React, { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import './Board.css';

interface Square {
  file: number;
  rank: number;
  piece: Piece | null;
  isLight: boolean;
}

interface Piece {
  type: 'pawn' | 'knight' | 'bishop' | 'rook' | 'queen' | 'king';
  color: 'white' | 'black';
}

interface BoardProps {
  fen: string;
  legalMoves: string[];
  lastMove?: { from: string; to: string };
  onMove: (from: string, to: string) => void;
  disabled?: boolean;
  perspective?: 'white' | 'black';
}

const PIECE_SYMBOLS: Record<string, { type: Piece['type']; color: Piece['color'] }> = {
  'P': { type: 'pawn', color: 'white' },
  'N': { type: 'knight', color: 'white' },
  'B': { type: 'bishop', color: 'white' },
  'R': { type: 'rook', color: 'white' },
  'Q': { type: 'queen', color: 'white' },
  'K': { type: 'king', color: 'white' },
  'p': { type: 'pawn', color: 'black' },
  'n': { type: 'knight', color: 'black' },
  'b': { type: 'bishop', color: 'black' },
  'r': { type: 'rook', color: 'black' },
  'q': { type: 'queen', color: 'black' },
  'k': { type: 'king', color: 'black' },
};

const PIECE_UNICODE: Record<string, string> = {
  'pawn_white': '♙', 'pawn_black': '♟',
  'knight_white': '♘', 'knight_black': '♞',
  'bishop_white': '♗', 'bishop_black': '♝',
  'rook_white': '♖', 'rook_black': '♜',
  'queen_white': '♕', 'queen_black': '♛',
  'king_white': '♔', 'king_black': '♚',
};

const Board: React.FC<BoardProps> = ({
  fen,
  legalMoves,
  lastMove,
  onMove,
  disabled = false,
  perspective = 'white',
}) => {
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [draggedFrom, setDraggedFrom] = useState<string | null>(null);

  // Parse FEN and create board
  const board = useMemo(() => {
    const squares: Square[] = [];
    const fenBoard = fen.split(' ')[0];
    const ranks = fenBoard.split('/');

    for (let rankIdx = 0; rankIdx < 8; rankIdx++) {
      let fileIdx = 0;
      for (const char of ranks[rankIdx]) {
        if (char >= '1' && char <= '8') {
          for (let i = 0; i < parseInt(char); i++) {
            const squareFile = fileIdx + i;
            squares.push({
              file: squareFile,
              rank: rankIdx,
              piece: null,
              isLight: (squareFile + rankIdx) % 2 === 0,
            });
          }
          fileIdx += parseInt(char);
        } else {
          const piece = PIECE_SYMBOLS[char];
          squares.push({
            file: fileIdx,
            rank: rankIdx,
            piece,
            isLight: (fileIdx + rankIdx) % 2 === 0,
          });
          fileIdx++;
        }
      }
    }

    return squares;
  }, [fen]);

  // Convert indices to algebraic notation
  const indexToAlgebraic = (file: number, rank: number): string => {
    return String.fromCharCode(97 + file) + (8 - rank);
  };

  // Get available moves from selected square
  const availableMoves = useMemo(() => {
    if (!selectedSquare) return [];
    return legalMoves
      .filter((move) => move.startsWith(selectedSquare))
      .map((move) => move.slice(2, 4));
  }, [selectedSquare, legalMoves]);

  // Handle square click
  const handleSquareClick = (file: number, rank: number) => {
    const square = indexToAlgebraic(file, rank);

    if (disabled) return;

    if (selectedSquare) {
      if (square === selectedSquare) {
        setSelectedSquare(null);
      } else if (availableMoves.includes(square)) {
        onMove(selectedSquare, square);
        setSelectedSquare(null);
      } else {
        setSelectedSquare(square);
      }
    } else {
      setSelectedSquare(square);
    }
  };

  // Handle drag and drop
  const handleDragStart = (e: React.DragEvent, square: string) => {
    if (disabled) return;
    setDraggedFrom(square);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, file: number, rank: number) => {
    e.preventDefault();
    if (!draggedFrom || disabled) return;

    const to = indexToAlgebraic(file, rank);
    if (availableMoves.includes(to)) {
      onMove(draggedFrom, to);
    }
    setDraggedFrom(null);
  };

  return (
    <div className="board-container">
      <div className="board">
        {board.map((square, idx) => {
          const squareNotation = indexToAlgebraic(square.file, square.rank);
          const isSelected = squareNotation === selectedSquare;
          const isAvailable = availableMoves.includes(squareNotation);
          const isLastMove =
            lastMove &&
            (squareNotation === lastMove.from || squareNotation === lastMove.to);

          return (
            <motion.div
              key={idx}
              className={`square ${square.isLight ? 'light' : 'dark'} ${
                isSelected ? 'selected' : ''
              } ${isAvailable ? 'available' : ''} ${
                isLastMove ? 'last-move' : ''
              }`}
              onClick={() => handleSquareClick(square.file, square.rank)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, square.file, square.rank)}
              whileHover={{ scale: 1.02 }}
            >
              {/* Rank and file labels */}
              {square.file === 0 && (
                <span className="rank-label">{8 - square.rank}</span>
              )}
              {square.rank === 7 && (
                <span className="file-label">
                  {String.fromCharCode(97 + square.file)}
                </span>
              )}

              {/* Piece */}
              {square.piece && (
                <motion.div
                  className={`piece ${square.piece.color}`}
                  draggable
                  onDragStart={(e) => handleDragStart(e, squareNotation)}
                  whileHover={{ scale: 1.1 }}
                  whileDrag={{ scale: 0.9, zIndex: 1000 }}
                >
                  {PIECE_UNICODE[`${square.piece.type}_${square.piece.color}`]}
                </motion.div>
              )}

              {/* Move indicator */}
              {isAvailable && (
                <div className="move-indicator">
                  {square.piece ? (
                    <div className="capture-indicator" />
                  ) : (
                    <div className="dot" />
                  )}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default Board;
