"""
Board representation using 0x88 or Bitboard hybrid approach
This module provides efficient board representation and square indexing
"""
from enum import Enum
from typing import Optional, Set, List, Tuple
import copy

# ═════════════════════════════════════════════════════════════════
# CONSTANTS
# ═════════════════════════════════════════════════════════════════

class Color(Enum):
    WHITE = 0
    BLACK = 1

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class CastleRights(Enum):
    WK = 1  # White King-side
    WQ = 2  # White Queen-side
    BK = 4  # Black King-side
    BQ = 8  # Black Queen-side

# Piece encoding: (color << 3) | piece_type
def encode_piece(color: Color, piece_type: PieceType) -> int:
    """Encode piece as integer"""
    if piece_type == PieceType.PAWN:
        return (color.value << 3) | 1
    return (color.value << 3) | piece_type.value

def decode_piece(piece: int) -> Tuple[Color, PieceType]:
    """Decode piece from integer"""
    color = Color(piece >> 3)
    ptype = PieceType(piece & 7)
    return color, ptype

# ═════════════════════════════════════════════════════════════════
# SQUARE INDEXING
# ═════════════════════════════════════════════════════════════════

def sq2idx(notation: str) -> int:
    """Convert algebraic notation (e.g., 'e4') to board index (0-63)"""
    if len(notation) != 2:
        raise ValueError(f"Invalid square notation: {notation}")
    col = ord(notation[0]) - ord('a')
    row = 8 - int(notation[1])
    if not (0 <= col < 8 and 0 <= row < 8):
        raise ValueError(f"Square out of bounds: {notation}")
    return row * 8 + col

def idx2sq(idx: int) -> str:
    """Convert board index (0-63) to algebraic notation"""
    if not (0 <= idx < 64):
        raise ValueError(f"Index out of bounds: {idx}")
    row = idx // 8
    col = idx % 8
    return chr(ord('a') + col) + str(8 - row)

def pos2sq(row: int, col: int) -> str:
    """Convert (row, col) to algebraic notation"""
    return idx2sq(row * 8 + col)

def sq2pos(notation: str) -> Tuple[int, int]:
    """Convert algebraic notation to (row, col)"""
    idx = sq2idx(notation)
    return idx // 8, idx % 8

# ═════════════════════════════════════════════════════════════════
# BOARD REPRESENTATION
# ═════════════════════════════════════════════════════════════════

class Board:
    """Efficient board representation"""
    
    def __init__(self):
        """Initialize standard chess position"""
        self.squares = [0] * 64  # 0 = empty
        self.turn = Color.WHITE
        self.castling = {
            "K": True,  # White King-side
            "Q": True,  # White Queen-side
            "k": True,  # Black King-side
            "q": True,  # Black Queen-side
        }
        self.en_passant: Optional[int] = None  # Square index for en passant
        self.halfmove_clock = 0  # For 50-move rule
        self.fullmove_number = 1
        self._init_standard()
    
    def _init_standard(self):
        """Set up standard starting position"""
        # Black back rank
        self.squares[0] = encode_piece(Color.BLACK, PieceType.ROOK)
        self.squares[1] = encode_piece(Color.BLACK, PieceType.KNIGHT)
        self.squares[2] = encode_piece(Color.BLACK, PieceType.BISHOP)
        self.squares[3] = encode_piece(Color.BLACK, PieceType.QUEEN)
        self.squares[4] = encode_piece(Color.BLACK, PieceType.KING)
        self.squares[5] = encode_piece(Color.BLACK, PieceType.BISHOP)
        self.squares[6] = encode_piece(Color.BLACK, PieceType.KNIGHT)
        self.squares[7] = encode_piece(Color.BLACK, PieceType.ROOK)
        
        # Black pawns
        for i in range(8, 16):
            self.squares[i] = encode_piece(Color.BLACK, PieceType.PAWN)
        
        # White pawns
        for i in range(48, 56):
            self.squares[i] = encode_piece(Color.WHITE, PieceType.PAWN)
        
        # White back rank
        self.squares[56] = encode_piece(Color.WHITE, PieceType.ROOK)
        self.squares[57] = encode_piece(Color.WHITE, PieceType.KNIGHT)
        self.squares[58] = encode_piece(Color.WHITE, PieceType.BISHOP)
        self.squares[59] = encode_piece(Color.WHITE, PieceType.QUEEN)
        self.squares[60] = encode_piece(Color.WHITE, PieceType.KING)
        self.squares[61] = encode_piece(Color.WHITE, PieceType.BISHOP)
        self.squares[62] = encode_piece(Color.WHITE, PieceType.KNIGHT)
        self.squares[63] = encode_piece(Color.WHITE, PieceType.ROOK)
    
    def copy(self) -> 'Board':
        """Create deep copy of board"""
        new_board = Board.__new__(Board)
        new_board.squares = self.squares.copy()
        new_board.turn = self.turn
        new_board.castling = self.castling.copy()
        new_board.en_passant = self.en_passant
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        return new_board
    
    def get_piece(self, row: int, col: int) -> Optional[Tuple[Color, PieceType]]:
        """Get piece at position"""
        if not (0 <= row < 8 and 0 <= col < 8):
            return None
        idx = row * 8 + col
        piece = self.squares[idx]
        if piece == 0:
            return None
        return decode_piece(piece)
    
    def set_piece(self, row: int, col: int, piece: Optional[Tuple[Color, PieceType]]):
        """Set piece at position"""
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError(f"Position out of bounds: ({row}, {col})")
        idx = row * 8 + col
        if piece is None:
            self.squares[idx] = 0
        else:
            color, ptype = piece
            self.squares[idx] = encode_piece(color, ptype)
    
    def is_empty(self, row: int, col: int) -> bool:
        """Check if square is empty"""
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        return self.squares[row * 8 + col] == 0
    
    def find_piece(self, color: Color, piece_type: PieceType) -> List[Tuple[int, int]]:
        """Find all pieces of given type and color"""
        result = []
        target = encode_piece(color, piece_type)
        for idx, piece in enumerate(self.squares):
            if piece == target:
                result.append((idx // 8, idx % 8))
        return result
    
    def clear(self):
        """Clear the board"""
        self.squares = [0] * 64
        self.en_passant = None
        self.halfmove_clock = 0
