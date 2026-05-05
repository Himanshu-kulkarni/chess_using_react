"""
Zobrist hashing for transposition tables
Provides efficient position hashing for alpha-beta search
"""
import random
from typing import Dict, Optional, Tuple
from .board import Board, Color, PieceType, sq2idx

class TranspositionEntry:
    """Entry in transposition table"""
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2
    
    def __init__(self, depth: int, score: int, flag: int, move: Optional[str] = None):
        self.depth = depth
        self.score = score
        self.flag = flag
        self.move = move

class ZobristHashing:
    """Zobrist hashing for position representation"""
    
    def __init__(self, seed: int = 12345):
        """Initialize Zobrist random numbers"""
        random.seed(seed)
        
        # Zobrist numbers for pieces
        # [color][piece_type][square] - 64 squares
        self.piece_hashes = {}
        for color in [Color.WHITE, Color.BLACK]:
            for ptype in PieceType:
                self.piece_hashes[(color.value, ptype.value)] = [random.getrandbits(64) for _ in range(64)]
        
        # Zobrist numbers for side to move
        self.side_hash = random.getrandbits(64)
        
        # Zobrist numbers for castling rights
        self.castling_hashes = {
            "K": random.getrandbits(64),
            "Q": random.getrandbits(64),
            "k": random.getrandbits(64),
            "q": random.getrandbits(64),
        }
        
        # Zobrist numbers for en passant files (0-7)
        self.en_passant_hashes = [random.getrandbits(64) for _ in range(8)]
    
    def hash_position(self, board: Board) -> int:
        """Generate Zobrist hash for current position"""
        h = 0
        
        # Hash pieces
        for idx in range(64):
            piece = board.squares[idx]
            if piece != 0:
                color = piece >> 3
                ptype = piece & 7
                h ^= self.piece_hashes[(color, ptype)][idx]
        
        # Hash side to move
        if board.turn == Color.BLACK:
            h ^= self.side_hash
        
        # Hash castling rights
        for right in ["K", "Q", "k", "q"]:
            if board.castling[right]:
                h ^= self.castling_hashes[right]
        
        # Hash en passant
        if board.en_passant is not None:
            ep_file = board.en_passant % 8
            h ^= self.en_passant_hashes[ep_file]
        
        return h

class TranspositionTable:
    """Transposition table for storing evaluated positions"""
    
    def __init__(self, max_size: int = 1_000_000):
        """Initialize transposition table"""
        self.max_size = max_size
        self.table: Dict[int, TranspositionEntry] = {}
        self.zobrist = ZobristHashing()
        self.access_count = 0
        self.hit_count = 0
    
    def store(self, board: Board, depth: int, score: int, flag: int, move: Optional[str] = None):
        """Store position in transposition table"""
        if len(self.table) >= self.max_size:
            # Simple replacement strategy: clear half the table
            if len(self.table) > self.max_size * 1.2:
                self.clear()
        
        h = self.zobrist.hash_position(board)
        entry = TranspositionEntry(depth, score, flag, move)
        self.table[h] = entry
    
    def lookup(self, board: Board) -> Optional[TranspositionEntry]:
        """Look up position in transposition table"""
        self.access_count += 1
        h = self.zobrist.hash_position(board)
        
        if h in self.table:
            self.hit_count += 1
            return self.table[h]
        
        return None
    
    def clear(self):
        """Clear transposition table"""
        self.table.clear()
        self.access_count = 0
        self.hit_count = 0
    
    def get_hit_rate(self) -> float:
        """Get transposition table hit rate"""
        if self.access_count == 0:
            return 0.0
        return self.hit_count / self.access_count
    
    def get_size_mb(self) -> float:
        """Get approximate size in MB"""
        # Rough estimate: each entry ~64 bytes
        return len(self.table) * 64 / (1024 * 1024)
