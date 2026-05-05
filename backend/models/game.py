"""
Game state management
"""
from typing import Optional, List, Dict
from enum import Enum
import uuid
import string
import random
from datetime import datetime, timedelta

from engine import Board, Move, MoveGenerator, ChessEngine, FENParser, Color, PieceType
from .database import Game, GameStatus, GameResult, TimeControl

class GameMode(str, Enum):
    vs_ai = "vs_ai"
    local_2player = "local_2player"
    online_multiplayer = "online"

class GameState:
    """In-memory game state"""
    
    def __init__(self, game_id: str, white_player: str, black_player: Optional[str] = None,
                 time_control: TimeControl = TimeControl.RAPID, ai_difficulty: Optional[str] = None):
        self.game_id = game_id
        self.white_player = white_player
        self.black_player = black_player or "AI"
        self.time_control = time_control
        self.ai_difficulty = ai_difficulty or "medium"
        
        # Board state
        self.board = Board()
        self.move_history: List[Move] = []
        self.fen_history: List[str] = []
        
        # Time management
        self.time_controls_ms = {
            TimeControl.BLITZ: 180_000,      # 3 min
            TimeControl.RAPID: 600_000,      # 10 min
            TimeControl.CLASSICAL: 3_600_000, # 1 hour
        }
        
        self.white_time = self.time_controls_ms[time_control]
        self.black_time = self.time_controls_ms[time_control]
        self.increment = 0  # milliseconds per move
        
        self.last_move_time = datetime.utcnow()
        
        # Game state
        self.is_active = True
        self.is_finished = False
        self.result: Optional[GameResult] = None
        self.status = GameStatus.IN_PROGRESS
        
        # AI
        self.engine: Optional[ChessEngine] = None
        if black_player == "AI":
            self.engine = ChessEngine()
    
    def make_move(self, move: Move, player: str) -> bool:
        """
        Make a move
        
        Returns:
            True if move was legal, False otherwise
        """
        # Validate it's the right player's turn
        if self.board.turn == Color.WHITE and player != self.white_player:
            return False
        if self.board.turn == Color.BLACK and player != self.black_player:
            return False
        
        # Check if move is legal
        legal_moves = MoveGenerator.generate_legal_moves(self.board, self.board.turn)
        if move not in legal_moves:
            return False
        
        # Save state before move
        self.fen_history.append(FENParser.to_fen(self.board))
        
        # Make the move
        MoveGenerator.make_move(self.board, move)
        self.move_history.append(move)
        
        # Update time
        self._update_time(player)
        
        # Check game end conditions
        self._check_game_end()
        
        return True
    
    def _update_time(self, player: str):
        """Update time remaining after move"""
        now = datetime.utcnow()
        elapsed = (now - self.last_move_time).total_seconds() * 1000
        
        if player == self.white_player:
            self.white_time -= elapsed
            self.white_time += self.increment
        else:
            self.black_time -= elapsed
            self.black_time += self.increment
        
        self.last_move_time = now
        
        # Check for timeout
        if self.white_time < 0:
            self.result = GameResult.BLACK_WIN
            self.is_finished = True
        elif self.black_time < 0:
            self.result = GameResult.WHITE_WIN
            self.is_finished = True
    
    def _check_game_end(self):
        """Check for checkmate, stalemate, etc."""
        legal_moves = MoveGenerator.generate_legal_moves(self.board, self.board.turn)
        
        if not legal_moves:
            if MoveGenerator.is_in_check(self.board, self.board.turn):
                # Checkmate
                if self.board.turn == Color.WHITE:
                    self.result = GameResult.BLACK_WIN
                else:
                    self.result = GameResult.WHITE_WIN
            else:
                # Stalemate
                self.result = GameResult.DRAW
            
            self.is_finished = True
        
        # Check 50-move rule
        if self.board.halfmove_clock >= 100:
            self.result = GameResult.DRAW
            self.is_finished = True
    
    def resign(self, player: str):
        """Player resigns"""
        if player == self.white_player:
            self.result = GameResult.BLACK_WIN
        else:
            self.result = GameResult.WHITE_WIN
        
        self.is_finished = True
    
    def offer_draw(self) -> bool:
        """Offer draw"""
        if not self.is_active or self.is_finished:
            return False
        # Would need to implement draw offer acceptance
        return True
    
    def accept_draw(self):
        """Accept draw"""
        self.result = GameResult.DRAW
        self.is_finished = True
    
    def undo_move(self) -> bool:
        """Undo last move"""
        if not self.move_history or len(self.fen_history) < 1:
            return False
        
        # Restore previous FEN
        fen = self.fen_history.pop()
        self.board = FENParser.from_fen(fen)
        
        # Remove from history
        self.move_history.pop()
        
        return True
    
    def get_legal_moves(self) -> List[Move]:
        """Get all legal moves for current position"""
        return MoveGenerator.generate_legal_moves(self.board, self.board.turn)
    
    def get_ai_move(self) -> Optional[Move]:
        """Get AI's best move"""
        if not self.engine:
            return None
        
        depth_map = {
            "easy": 3,
            "medium": 5,
            "hard": 7,
        }
        
        depth = depth_map.get(self.ai_difficulty, 5)
        return self.engine.search(self.board, max_depth=depth, max_time=2.0)
    
    def to_dict(self) -> dict:
        """Serialize game state"""
        return {
            "game_id": self.game_id,
            "white_player": self.white_player,
            "black_player": self.black_player,
            "fen": FENParser.to_fen(self.board),
            "moves": [str(m) for m in self.move_history],
            "white_time": self.white_time,
            "black_time": self.black_time,
            "is_finished": self.is_finished,
            "result": self.result.value if self.result else None,
            "current_turn": "white" if self.board.turn == Color.WHITE else "black",
        }

class GameManager:
    """Manages active games"""
    
    def __init__(self):
        self.games: Dict[str, GameState] = {}
    
    def create_game(self, white_player: str, black_player: Optional[str] = None,
                   time_control: TimeControl = TimeControl.RAPID,
                   ai_difficulty: Optional[str] = None) -> GameState:
        """Create new game"""
        game_id = str(uuid.uuid4())[:8]
        game = GameState(game_id, white_player, black_player, time_control, ai_difficulty)
        self.games[game_id] = game
        return game
    
    def get_game(self, game_id: str) -> Optional[GameState]:
        """Get game by ID"""
        return self.games.get(game_id)
    
    def end_game(self, game_id: str) -> bool:
        """End game"""
        game = self.games.get(game_id)
        if game:
            game.is_active = False
            return True
        return False
    
    def generate_room_code(self, length: int = 6) -> str:
        """Generate random room code"""
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Global game manager
game_manager = GameManager()
