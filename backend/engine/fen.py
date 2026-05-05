"""
FEN (Forsyth-Edwards Notation) support for chess positions
"""
from .board import Board, Color, PieceType, encode_piece, sq2idx
from typing import Optional

class FENParser:
    """Parse and generate FEN strings"""
    
    PIECE_SYMBOLS = {
        "P": (Color.WHITE, PieceType.PAWN),
        "N": (Color.WHITE, PieceType.KNIGHT),
        "B": (Color.WHITE, PieceType.BISHOP),
        "R": (Color.WHITE, PieceType.ROOK),
        "Q": (Color.WHITE, PieceType.QUEEN),
        "K": (Color.WHITE, PieceType.KING),
        "p": (Color.BLACK, PieceType.PAWN),
        "n": (Color.BLACK, PieceType.KNIGHT),
        "b": (Color.BLACK, PieceType.BISHOP),
        "r": (Color.BLACK, PieceType.ROOK),
        "q": (Color.BLACK, PieceType.QUEEN),
        "k": (Color.BLACK, PieceType.KING),
    }
    
    PIECE_TO_CHAR = {v: k for k, v in PIECE_SYMBOLS.items()}
    
    @staticmethod
    def from_fen(fen: str) -> Board:
        """
        Parse FEN string and create board
        Format: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
        """
        parts = fen.strip().split()
        if len(parts) != 6:
            raise ValueError(f"Invalid FEN: {fen}")
        
        board_str, turn_str, castling_str, ep_str, halfmove_str, fullmove_str = parts
        
        board = Board()
        board.clear()
        
        # Parse board
        row = 0
        col = 0
        for char in board_str:
            if char == "/":
                row += 1
                col = 0
            elif char.isdigit():
                col += int(char)
            else:
                if char in FENParser.PIECE_SYMBOLS:
                    color, ptype = FENParser.PIECE_SYMBOLS[char]
                    board.set_piece(row, col, (color, ptype))
                    col += 1
        
        # Parse turn
        board.turn = Color.WHITE if turn_str == "w" else Color.BLACK
        
        # Parse castling rights
        board.castling = {
            "K": "K" in castling_str,
            "Q": "Q" in castling_str,
            "k": "k" in castling_str,
            "q": "q" in castling_str,
        }
        
        # Parse en passant
        if ep_str != "-":
            board.en_passant = sq2idx(ep_str)
        else:
            board.en_passant = None
        
        # Parse move counters
        board.halfmove_clock = int(halfmove_str)
        board.fullmove_number = int(fullmove_str)
        
        return board
    
    @staticmethod
    def to_fen(board: Board) -> str:
        """Generate FEN string from board"""
        # Board representation
        board_str_parts = []
        for row in range(8):
            empty_count = 0
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        board_str_parts.append(str(empty_count))
                        empty_count = 0
                    color, ptype = piece
                    board_str_parts.append(FENParser.PIECE_TO_CHAR[(color, ptype)])
            if empty_count > 0:
                board_str_parts.append(str(empty_count))
            if row < 7:
                board_str_parts.append("/")
        
        board_str = "".join(board_str_parts)
        
        # Turn
        turn_str = "w" if board.turn == Color.WHITE else "b"
        
        # Castling rights
        castling_str = ""
        if board.castling["K"]:
            castling_str += "K"
        if board.castling["Q"]:
            castling_str += "Q"
        if board.castling["k"]:
            castling_str += "k"
        if board.castling["q"]:
            castling_str += "q"
        if not castling_str:
            castling_str = "-"
        
        # En passant
        if board.en_passant is not None:
            from .board import idx2sq
            ep_str = idx2sq(board.en_passant)
        else:
            ep_str = "-"
        
        # Combine
        return f"{board_str} {turn_str} {castling_str} {ep_str} {board.halfmove_clock} {board.fullmove_number}"
