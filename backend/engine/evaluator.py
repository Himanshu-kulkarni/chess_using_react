"""
Position evaluator with piece-square tables and advanced evaluation
"""
from .board import Board, Color, PieceType, sq2idx

class Evaluator:
    """Advanced position evaluator"""
    
    # Piece values
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000,  # High value to avoid capture
    }
    
    # Piece-square tables (PST)
    # Values are for white; flip for black
    PST = {
        PieceType.PAWN: [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [ 5,  5, 10, 25, 25, 10,  5,  5],
            [ 0,  0,  0, 20, 20,  0,  0,  0],
            [ 5, -5,-10,  0,  0,-10, -5,  5],
            [ 5, 10, 10,-20,-20, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
        ],
        PieceType.KNIGHT: [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50],
        ],
        PieceType.BISHOP: [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20],
        ],
        PieceType.ROOK: [
            [ 0,  0,  0,  5,  5,  0,  0,  0],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [ 5, 10, 10, 10, 10, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
        ],
        PieceType.QUEEN: [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20],
        ],
        PieceType.KING: [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [  0,-10,-10,-10,-10,-10,-10,  0],
            [ 10,  0,  0,  0,  0,  0,  0, 10],
            [ 20, 10, 10,  0,  0, 10, 10, 20],
            [ 20, 30, 10,  0,  0, 10, 30, 20],
            [ 20, 40, 40, 10, 10, 40, 40, 20],
        ],
    }
    
    @staticmethod
    def evaluate(board: Board) -> int:
        """
        Evaluate position from white's perspective.
        Positive = white advantage, negative = black advantage
        """
        score = 0
        
        # Material and piece-square table evaluation
        for idx in range(64):
            piece = board.squares[idx]
            if piece == 0:
                continue
            
            color = Color(piece >> 3)
            ptype = PieceType(piece & 7)
            row, col = idx // 8, idx % 8
            
            # Piece value
            piece_val = Evaluator.PIECE_VALUES[ptype]
            
            # Piece-square table value
            pst_table = Evaluator.PST[ptype]
            if color == Color.WHITE:
                pst_val = pst_table[7 - row][col]
            else:
                pst_val = pst_table[row][col]
            
            total_val = piece_val + pst_val
            
            if color == Color.WHITE:
                score += total_val
            else:
                score -= total_val
        
        # Advanced evaluation features
        score += Evaluator._evaluate_mobility(board)
        score += Evaluator._evaluate_pawn_structure(board)
        score += Evaluator._evaluate_king_safety(board)
        
        return score
    
    @staticmethod
    def _evaluate_mobility(board: Board) -> int:
        """Bonus for piece mobility"""
        from .move import MoveGenerator
        
        white_moves = len(MoveGenerator.generate_legal_moves(board, Color.WHITE))
        
        board.turn = Color.BLACK
        black_moves = len(MoveGenerator.generate_legal_moves(board, Color.BLACK))
        board.turn = Color.WHITE
        
        # Mobility bonus
        return (white_moves - black_moves) * 5
    
    @staticmethod
    def _evaluate_pawn_structure(board: Board) -> int:
        """Evaluate pawn structure (doubled, isolated, passed pawns)"""
        score = 0
        
        # Check for doubled pawns
        for col in range(8):
            white_pawns = 0
            black_pawns = 0
            
            for row in range(8):
                piece = board.squares[row * 8 + col]
                if piece == 0:
                    continue
                
                color = Color(piece >> 3)
                ptype = PieceType(piece & 7)
                
                if ptype == PieceType.PAWN:
                    if color == Color.WHITE:
                        white_pawns += 1
                    else:
                        black_pawns += 1
            
            # Penalty for doubled pawns
            if white_pawns > 1:
                score -= 20 * (white_pawns - 1)
            if black_pawns > 1:
                score += 20 * (black_pawns - 1)
        
        return score
    
    @staticmethod
    def _evaluate_king_safety(board: Board) -> int:
        """Evaluate king safety"""
        score = 0
        
        # Find kings
        white_king = board.find_piece(Color.WHITE, PieceType.KING)
        black_king = board.find_piece(Color.BLACK, PieceType.KING)
        
        if not white_king or not black_king:
            return 0
        
        w_row, w_col = white_king[0]
        b_row, b_col = black_king[0]
        
        # Bonus for castling rights
        if board.castling["K"] or board.castling["Q"]:
            score += 30
        if board.castling["k"] or board.castling["q"]:
            score -= 30
        
        # Penalty for exposed king
        if 2 <= w_col <= 5 and w_row < 6:  # King in center
            score -= 15
        if 2 <= b_col <= 5 and b_row > 1:  # King in center
            score += 15
        
        return score
