"""
PGN (Portable Game Notation) support for chess games
"""
import re
from typing import List, Optional, Dict, Tuple
from .board import Board, Color, PieceType
from .move import Move, MoveGenerator
from .fen import FENParser

class PGNGame:
    """Represents a chess game in PGN format"""
    
    def __init__(self):
        self.headers: Dict[str, str] = {
            "Event": "?",
            "Site": "?",
            "Date": "?",
            "Round": "?",
            "White": "?",
            "Black": "?",
            "Result": "*",
        }
        self.moves: List[Tuple[Move, str]] = []  # (Move object, algebraic notation)
        self.comments: Dict[int, str] = {}  # Move number -> comment
        self.variations: Dict[int, List[Move]] = {}  # Move number -> variations
    
    def set_header(self, key: str, value: str):
        """Set PGN header"""
        self.headers[key] = value
    
    def add_move(self, move: Move, notation: Optional[str] = None):
        """Add move to game"""
        if notation is None:
            notation = str(move)
        self.moves.append((move, notation))
    
    def get_pgn_string(self) -> str:
        """Generate PGN string"""
        lines = []
        
        # Headers
        for key, value in self.headers.items():
            lines.append(f'[{key} "{value}"]')
        
        lines.append("")
        
        # Moves (in rows of alternating white/black)
        move_lines = []
        for i, (move, notation) in enumerate(self.moves):
            move_num = i // 2 + 1
            if i % 2 == 0:
                move_lines.append(f"{move_num}. {notation}")
            else:
                move_lines[-1] += f" {notation}"
        
        lines.extend(move_lines)
        
        # Result
        lines.append(self.headers["Result"])
        
        return "\n".join(lines)

class PGNParser:
    """Parse PGN strings into games"""
    
    @staticmethod
    def parse(pgn_string: str) -> PGNGame:
        """
        Parse PGN string
        Returns: PGNGame object
        """
        game = PGNGame()
        lines = pgn_string.strip().split("\n")
        
        i = 0
        # Parse headers
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            if line.startswith("["):
                # Parse header
                match = re.match(r'\[(\w+)\s"([^"]*)"\]', line)
                if match:
                    key, value = match.groups()
                    game.set_header(key, value)
                i += 1
            else:
                break
        
        # Parse moves
        board = Board()
        move_text = " ".join(lines[i:])
        
        # Remove comments
        move_text = re.sub(r'\{[^}]*\}', '', move_text)
        move_text = re.sub(r'\([^)]*\)', '', move_text)
        
        # Split into tokens
        tokens = move_text.split()
        
        for token in tokens:
            # Skip move numbers and results
            if token.endswith(".") or token in ["1-0", "0-1", "1/2-1/2", "*"]:
                continue
            
            # Parse move notation
            move = PGNParser._parse_algebraic(board, token)
            if move:
                game.add_move(move, token)
                MoveGenerator.make_move(board, move)
        
        return game
    
    @staticmethod
    def _parse_algebraic(board: Board, notation: str) -> Optional[Move]:
        """
        Parse algebraic notation (e.g., e4, Nf3, Qh5+, O-O)
        Simplified parser - does not handle all edge cases
        """
        notation = notation.strip()
        
        # Remove check/checkmate symbols
        notation = notation.rstrip("+#!")
        
        # Castling
        if notation == "O-O":
            if board.turn == Color.WHITE:
                return Move("e1", "g1")
            else:
                return Move("e8", "g8")
        elif notation == "O-O-O":
            if board.turn == Color.WHITE:
                return Move("e1", "c1")
            else:
                return Move("e8", "c8")
        
        # Pawn move
        if notation[0].islower():
            # e4, exd5, e8=Q, exd8=Q
            file = notation[0]
            
            if "x" in notation:
                # Capture
                capture_idx = notation.index("x")
                to_sq = notation[capture_idx + 1:capture_idx + 3]
                # Find pawn
                from_col = ord(file) - ord("a")
                
                legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
                for move in legal_moves:
                    if move.to_sq == to_sq and move.from_idx % 8 == from_col:
                        piece = board.squares[move.from_idx]
                        if (piece & 7) == PieceType.PAWN.value:
                            return move
            else:
                # Non-capture
                to_sq = notation[-2:]
                
                legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
                for move in legal_moves:
                    if move.to_sq == to_sq:
                        piece = board.squares[move.from_idx]
                        if (piece & 7) == PieceType.PAWN.value:
                            return move
        
        else:
            # Piece move
            piece_char = notation[0]
            piece_map = {"N": PieceType.KNIGHT, "B": PieceType.BISHOP, 
                        "R": PieceType.ROOK, "Q": PieceType.QUEEN, "K": PieceType.KING}
            
            if piece_char not in piece_map:
                return None
            
            ptype = piece_map[piece_char]
            
            # Extract target square (last 2 chars)
            to_sq = notation[-2:]
            
            # Find matching move
            legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
            matches = []
            
            for move in legal_moves:
                if move.to_sq == to_sq:
                    piece = board.squares[move.from_idx]
                    if (piece & 7) == ptype.value:
                        matches.append(move)
            
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                # Disambiguation needed - use middle part of notation
                disamb = notation[1:-2]
                for move in matches:
                    if disamb in move.from_sq:
                        return move
                # Default to first match
                return matches[0]
        
        return None
