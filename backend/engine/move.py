"""
Move generation and validation
Includes all move types: quiet moves, captures, castling, en passant, pawn promotion
"""
from typing import List, Tuple, Optional
from .board import Board, Color, PieceType, encode_piece, decode_piece, idx2sq, sq2idx

class Move:
    """Represents a chess move"""
    
    def __init__(self, from_sq: str, to_sq: str, promotion: Optional[PieceType] = None):
        """Create a move (e.g., 'e2e4')"""
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.promotion = promotion
        self.from_idx = sq2idx(from_sq)
        self.to_idx = sq2idx(to_sq)
    
    def __repr__(self):
        if self.promotion:
            pname = self.promotion.name[0].lower()
            return f"{self.from_sq}{self.to_sq}{pname}"
        return f"{self.from_sq}{self.to_sq}"
    
    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.from_sq == other.from_sq and 
                self.to_sq == other.to_sq and 
                self.promotion == other.promotion)
    
    def __hash__(self):
        return hash((self.from_sq, self.to_sq, self.promotion))

# ═════════════════════════════════════════════════════════════════
# MOVE GENERATION
# ═════════════════════════════════════════════════════════════════

class MoveGenerator:
    """Generates legal moves for a position"""
    
    @staticmethod
    def generate_pseudo_legal(board: Board, color: Color) -> List[Move]:
        """Generate all pseudo-legal moves (doesn't check for leaving king in check)"""
        moves = []
        
        for idx in range(64):
            piece = board.squares[idx]
            if piece == 0:
                continue
            
            p_color = Color(piece >> 3)
            if p_color != color:
                continue
            
            p_type = PieceType(piece & 7)
            row, col = idx // 8, idx % 8
            
            if p_type == PieceType.PAWN:
                MoveGenerator._gen_pawn_moves(board, row, col, color, moves)
            elif p_type == PieceType.KNIGHT:
                MoveGenerator._gen_knight_moves(board, row, col, color, moves)
            elif p_type == PieceType.BISHOP:
                MoveGenerator._gen_bishop_moves(board, row, col, color, moves)
            elif p_type == PieceType.ROOK:
                MoveGenerator._gen_rook_moves(board, row, col, color, moves)
            elif p_type == PieceType.QUEEN:
                MoveGenerator._gen_queen_moves(board, row, col, color, moves)
            elif p_type == PieceType.KING:
                MoveGenerator._gen_king_moves(board, row, col, color, moves)
        
        return moves
    
    @staticmethod
    def _gen_pawn_moves(board: Board, row: int, col: int, color: Color, moves: List[Move]):
        """Generate pawn moves"""
        direction = -1 if color == Color.WHITE else 1
        start_row = 6 if color == Color.WHITE else 1
        promotion_row = 0 if color == Color.WHITE else 7
        
        # Single push
        new_row = row + direction
        if 0 <= new_row < 8:
            if board.squares[new_row * 8 + col] == 0:
                from_sq = idx2sq(row * 8 + col)
                to_sq = idx2sq(new_row * 8 + col)
                
                if new_row == promotion_row:
                    # Promotion
                    for ptype in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                        moves.append(Move(from_sq, to_sq, ptype))
                else:
                    moves.append(Move(from_sq, to_sq))
                
                # Double push from start
                if row == start_row:
                    new_row2 = row + 2 * direction
                    if board.squares[new_row2 * 8 + col] == 0:
                        to_sq2 = idx2sq(new_row2 * 8 + col)
                        moves.append(Move(from_sq, to_sq2))
        
        # Captures
        for dcol in [-1, 1]:
            new_col = col + dcol
            new_row = row + direction
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.squares[new_row * 8 + new_col]
                if target != 0:
                    target_color = Color(target >> 3)
                    if target_color != color:
                        from_sq = idx2sq(row * 8 + col)
                        to_sq = idx2sq(new_row * 8 + new_col)
                        
                        if new_row == promotion_row:
                            for ptype in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                                moves.append(Move(from_sq, to_sq, ptype))
                        else:
                            moves.append(Move(from_sq, to_sq))
                
                # En passant
                if board.en_passant and (new_row * 8 + new_col) == board.en_passant:
                    from_sq = idx2sq(row * 8 + col)
                    to_sq = idx2sq(new_row * 8 + new_col)
                    moves.append(Move(from_sq, to_sq))
    
    @staticmethod
    def _gen_knight_moves(board: Board, row: int, col: int, color: Color, moves: List[Move]):
        """Generate knight moves"""
        deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in deltas:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.squares[new_row * 8 + new_col]
                if target == 0 or Color(target >> 3) != color:
                    from_sq = idx2sq(row * 8 + col)
                    to_sq = idx2sq(new_row * 8 + new_col)
                    moves.append(Move(from_sq, to_sq))
    
    @staticmethod
    def _gen_sliding_moves(board: Board, row: int, col: int, color: Color, 
                          deltas: List[Tuple[int, int]], moves: List[Move]):
        """Generate sliding piece moves (bishop, rook, queen)"""
        for dr, dc in deltas:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.squares[r * 8 + c]
                if target == 0:
                    from_sq = idx2sq(row * 8 + col)
                    to_sq = idx2sq(r * 8 + c)
                    moves.append(Move(from_sq, to_sq))
                else:
                    target_color = Color(target >> 3)
                    if target_color != color:
                        from_sq = idx2sq(row * 8 + col)
                        to_sq = idx2sq(r * 8 + c)
                        moves.append(Move(from_sq, to_sq))
                    break
                r += dr
                c += dc
    
    @staticmethod
    def _gen_bishop_moves(board: Board, row: int, col: int, color: Color, moves: List[Move]):
        """Generate bishop moves"""
        deltas = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        MoveGenerator._gen_sliding_moves(board, row, col, color, deltas, moves)
    
    @staticmethod
    def _gen_rook_moves(board: Board, row: int, col: int, color: Color, moves: List[Move]):
        """Generate rook moves"""
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        MoveGenerator._gen_sliding_moves(board, row, col, color, deltas, moves)
    
    @staticmethod
    def _gen_queen_moves(board: Board, row: int, col: int, color: Color, moves: List[Move]):
        """Generate queen moves"""
        deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        MoveGenerator._gen_sliding_moves(board, row, col, color, deltas, moves)
    
    @staticmethod
    def _gen_king_moves(board: Board, row: int, col: int, color: Color, moves: List[Move]):
        """Generate king moves including castling"""
        deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in deltas:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.squares[new_row * 8 + new_col]
                if target == 0 or Color(target >> 3) != color:
                    from_sq = idx2sq(row * 8 + col)
                    to_sq = idx2sq(new_row * 8 + new_col)
                    moves.append(Move(from_sq, to_sq))
        
        # Castling
        if color == Color.WHITE:
            if board.castling["K"] and board.is_empty(7, 5) and board.is_empty(7, 6):
                moves.append(Move("e1", "g1"))
            if board.castling["Q"] and board.is_empty(7, 3) and board.is_empty(7, 2) and board.is_empty(7, 1):
                moves.append(Move("e1", "c1"))
        else:
            if board.castling["k"] and board.is_empty(0, 5) and board.is_empty(0, 6):
                moves.append(Move("e8", "g8"))
            if board.castling["q"] and board.is_empty(0, 3) and board.is_empty(0, 2) and board.is_empty(0, 1):
                moves.append(Move("e8", "c8"))
    
    @staticmethod
    def is_in_check(board: Board, color: Color) -> bool:
        """Check if king is in check"""
        king_positions = board.find_piece(color, PieceType.KING)
        if not king_positions:
            return False
        
        king_row, king_col = king_positions[0]
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        # Check if any opponent piece can attack the king
        for idx in range(64):
            piece = board.squares[idx]
            if piece == 0:
                continue
            
            p_color = Color(piece >> 3)
            if p_color != opponent:
                continue
            
            p_type = PieceType(piece & 7)
            row, col = idx // 8, idx % 8
            
            if MoveGenerator._can_attack(board, row, col, king_row, king_col, p_type):
                return True
        
        return False
    
    @staticmethod
    def _can_attack(board: Board, from_row: int, from_col: int, to_row: int, to_col: int, piece_type: PieceType) -> bool:
        """Check if a piece can attack a given square"""
        if piece_type == PieceType.PAWN:
            color = Color(board.squares[from_row * 8 + from_col] >> 3)
            direction = -1 if color == Color.WHITE else 1
            return (to_row == from_row + direction and abs(to_col - from_col) == 1)
        elif piece_type == PieceType.KNIGHT:
            dr, dc = abs(to_row - from_row), abs(to_col - from_col)
            return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)
        elif piece_type == PieceType.BISHOP:
            return MoveGenerator._can_slide(board, from_row, from_col, to_row, to_col, 
                                          [(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif piece_type == PieceType.ROOK:
            return MoveGenerator._can_slide(board, from_row, from_col, to_row, to_col,
                                          [(-1, 0), (1, 0), (0, -1), (0, 1)])
        elif piece_type == PieceType.QUEEN:
            return MoveGenerator._can_slide(board, from_row, from_col, to_row, to_col,
                                          [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])
        elif piece_type == PieceType.KING:
            return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
        return False
    
    @staticmethod
    def _can_slide(board: Board, from_row: int, from_col: int, to_row: int, to_col: int,
                   deltas: List[Tuple[int, int]]) -> bool:
        """Check if a sliding piece can reach a square"""
        if not any((to_row - from_row, to_col - from_col) == (d[0], d[1]) or 
                   (to_row - from_row, to_col - from_col) == (-d[0], -d[1]) for d in deltas):
            return False
        
        # Find the direction
        dr = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        dc = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        # Check path is clear
        r, c = from_row + dr, from_col + dc
        while (r, c) != (to_row, to_col):
            if board.squares[r * 8 + c] != 0:
                return False
            r += dr
            c += dc
        
        return True
    
    @staticmethod
    def generate_legal_moves(board: Board, color: Color) -> List[Move]:
        """Generate all legal moves (excluding moves that leave king in check)"""
        pseudo_legal = MoveGenerator.generate_pseudo_legal(board, color)
        legal_moves = []
        
        for move in pseudo_legal:
            # Make move
            board_copy = board.copy()
            MoveGenerator.make_move(board_copy, move)
            
            # Check if king is safe
            if not MoveGenerator.is_in_check(board_copy, color):
                legal_moves.append(move)
        
        return legal_moves
    
    @staticmethod
    def make_move(board: Board, move: Move):
        """Apply move to board (MUTATES board)"""
        from_row, from_col = move.from_idx // 8, move.from_idx % 8
        to_row, to_col = move.to_idx // 8, move.to_idx % 8
        
        piece = board.squares[move.from_idx]
        if piece == 0:
            raise ValueError(f"No piece at {move.from_sq}")
        
        p_color = Color(piece >> 3)
        p_type = PieceType(piece & 7)
        
        # Handle en passant
        if p_type == PieceType.PAWN and board.en_passant and move.to_idx == board.en_passant:
            capture_idx = board.en_passant - 8 if p_color == Color.WHITE else board.en_passant + 8
            board.squares[capture_idx] = 0
        
        # Move piece
        board.squares[move.to_idx] = piece
        board.squares[move.from_idx] = 0
        
        # Handle pawn promotion
        if p_type == PieceType.PAWN and move.promotion:
            board.squares[move.to_idx] = encode_piece(p_color, move.promotion)
        
        # Handle castling
        if p_type == PieceType.KING:
            if move.from_sq == "e1" and move.to_sq == "g1":  # White king-side
                board.squares[sq2idx("h1")] = 0
                board.squares[sq2idx("f1")] = encode_piece(Color.WHITE, PieceType.ROOK)
            elif move.from_sq == "e1" and move.to_sq == "c1":  # White queen-side
                board.squares[sq2idx("a1")] = 0
                board.squares[sq2idx("d1")] = encode_piece(Color.WHITE, PieceType.ROOK)
            elif move.from_sq == "e8" and move.to_sq == "g8":  # Black king-side
                board.squares[sq2idx("h8")] = 0
                board.squares[sq2idx("f8")] = encode_piece(Color.BLACK, PieceType.ROOK)
            elif move.from_sq == "e8" and move.to_sq == "c8":  # Black queen-side
                board.squares[sq2idx("a8")] = 0
                board.squares[sq2idx("d8")] = encode_piece(Color.BLACK, PieceType.ROOK)
            
            # Remove castling rights
            if p_color == Color.WHITE:
                board.castling["K"] = board.castling["Q"] = False
            else:
                board.castling["k"] = board.castling["q"] = False
        
        # Handle rook captures/moves
        if p_type == PieceType.ROOK:
            if move.from_sq == "a1":
                board.castling["Q"] = False
            elif move.from_sq == "h1":
                board.castling["K"] = False
            elif move.from_sq == "a8":
                board.castling["q"] = False
            elif move.from_sq == "h8":
                board.castling["k"] = False
        
        # Update en passant
        if p_type == PieceType.PAWN and abs(to_row - from_row) == 2:
            board.en_passant = (from_row + to_row) // 2 * 8 + to_col
        else:
            board.en_passant = None
        
        # Update move counters
        if p_type == PieceType.PAWN or board.squares[move.to_idx] != 0:
            board.halfmove_clock = 0
        else:
            board.halfmove_clock += 1
        
        if p_color == Color.BLACK:
            board.fullmove_number += 1
        
        board.turn = Color.BLACK if board.turn == Color.WHITE else Color.WHITE
