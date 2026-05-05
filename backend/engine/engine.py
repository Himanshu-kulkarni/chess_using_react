"""
Main chess engine with iterative deepening, alpha-beta pruning, and quiescence search
"""
import time
import math
from typing import Optional, Tuple
from .board import Board, Color, PieceType
from .move import Move, MoveGenerator
from .evaluator import Evaluator
from .zobrist import TranspositionTable, TranspositionEntry

class ChessEngine:
    """Production-grade chess engine"""
    
    MATE_SCORE = 100000
    MAX_DEPTH = 32
    
    def __init__(self, transposition_table_size: int = 1_000_000):
        """Initialize engine"""
        self.tt = TranspositionTable(transposition_table_size)
        self.nodes_searched = 0
        self.max_time = 3.0  # seconds
        self.start_time = 0
        self.best_move = None
        self.best_score = 0
    
    def search(self, board: Board, max_depth: int = 5, max_time: float = 3.0) -> Optional[Move]:
        """
        Find best move using iterative deepening with alpha-beta pruning
        
        Args:
            board: Current board position
            max_depth: Maximum search depth
            max_time: Maximum time in seconds
        
        Returns:
            Best move found, or None if no legal moves
        """
        self.max_time = max_time
        self.start_time = time.time()
        self.nodes_searched = 0
        self.best_move = None
        self.best_score = 0
        
        # Get legal moves for current position
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
        if not legal_moves:
            return None
        
        # Iterative deepening
        for depth in range(1, max_depth + 1):
            if self._time_exceeded():
                break
            
            # Alpha-beta search at this depth
            score = self._alpha_beta(
                board, depth, -math.inf, math.inf, True
            )
            
            # Store best move if found
            if self.best_move:
                pass  # Already stored during search
        
        return self.best_move
    
    def _alpha_beta(self, board: Board, depth: int, alpha: float, beta: float, 
                   is_maximizing: bool) -> float:
        """
        Alpha-beta minimax with transposition tables and quiescence search
        """
        self.nodes_searched += 1
        
        # Check time limit
        if self.nodes_searched % 1000 == 0 and self._time_exceeded():
            return 0
        
        alpha_orig = alpha
        
        # Transposition table lookup
        tt_entry = self.tt.lookup(board)
        if tt_entry and tt_entry.depth >= depth:
            if tt_entry.flag == TranspositionEntry.EXACT:
                return tt_entry.score
            elif tt_entry.flag == TranspositionEntry.LOWER_BOUND:
                alpha = max(alpha, tt_entry.score)
            elif tt_entry.flag == TranspositionEntry.UPPER_BOUND:
                beta = min(beta, tt_entry.score)
            
            if alpha >= beta:
                return tt_entry.score
        
        # Terminal nodes
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
        
        if not legal_moves:
            # Checkmate or stalemate
            if MoveGenerator.is_in_check(board, board.turn):
                return -self.MATE_SCORE + (self.MAX_DEPTH - depth)
            else:
                return 0  # Stalemate
        
        # Quiescence search at leaf nodes
        if depth == 0:
            return self._quiescence(board, alpha, beta, 0)
        
        if is_maximizing:
            value = -math.inf
            best_move = None
            
            for move in legal_moves:
                board_copy = board.copy()
                MoveGenerator.make_move(board_copy, move)
                
                eval_score = self._alpha_beta(board_copy, depth - 1, alpha, beta, False)
                
                if eval_score > value:
                    value = eval_score
                    best_move = move
                    
                    # Store as best move if at root
                    if depth == 0 or (board_copy.turn == Color.WHITE and eval_score > self.best_score):
                        self.best_move = move
                        self.best_score = eval_score
                
                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # Beta cutoff
        else:
            value = math.inf
            best_move = None
            
            for move in legal_moves:
                board_copy = board.copy()
                MoveGenerator.make_move(board_copy, move)
                
                eval_score = self._alpha_beta(board_copy, depth - 1, alpha, beta, True)
                
                if eval_score < value:
                    value = eval_score
                    best_move = move
                
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cutoff
        
        # Store in transposition table
        flag = TranspositionEntry.EXACT
        if value <= alpha_orig:
            flag = TranspositionEntry.UPPER_BOUND
        elif value >= beta:
            flag = TranspositionEntry.LOWER_BOUND
        
        self.tt.store(board, depth, int(value), flag, str(best_move) if best_move else None)
        
        return value
    
    def _quiescence(self, board: Board, alpha: float, beta: float, depth: int) -> float:
        """
        Quiescence search to avoid horizon effect
        Only considers captures and checks
        """
        self.nodes_searched += 1
        
        # Static evaluation as base case
        eval_score = Evaluator.evaluate(board)
        
        if eval_score >= beta:
            return eval_score
        
        alpha = max(alpha, eval_score)
        
        if depth >= 3:  # Limit quiescence depth
            return eval_score
        
        # Get all moves and filter to captures + checks
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
        captures = []
        
        for move in legal_moves:
            # Check if it's a capture
            to_piece = board.squares[move.to_idx]
            is_capture = to_piece != 0
            
            if is_capture or move.promotion:  # Also include promotions
                captures.append(move)
        
        if not captures:
            return eval_score
        
        for move in captures:
            board_copy = board.copy()
            MoveGenerator.make_move(board_copy, move)
            
            eval_score = -self._quiescence(board_copy, -beta, -alpha, depth + 1)
            
            if eval_score >= beta:
                return eval_score
            
            alpha = max(alpha, eval_score)
        
        return alpha
    
    def _time_exceeded(self) -> bool:
        """Check if time limit exceeded"""
        elapsed = time.time() - self.start_time
        return elapsed >= self.max_time
    
    def get_stats(self) -> dict:
        """Get engine statistics"""
        elapsed = time.time() - self.start_time
        nps = self.nodes_searched / elapsed if elapsed > 0 else 0
        
        return {
            "nodes_searched": self.nodes_searched,
            "time_elapsed": elapsed,
            "nodes_per_second": int(nps),
            "tt_size_mb": self.tt.get_size_mb(),
            "tt_hit_rate": self.tt.get_hit_rate(),
            "best_move": str(self.best_move),
            "best_score": self.best_score,
        }
