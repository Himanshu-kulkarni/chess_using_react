"""
Database models using SQLAlchemy ORM
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class GameStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class GameResult(str, enum.Enum):
    WHITE_WIN = "white_win"
    BLACK_WIN = "black_win"
    DRAW = "draw"
    ABANDONED = "abandoned"

class TimeControl(str, enum.Enum):
    BLITZ = "blitz"          # 3 min
    RAPID = "rapid"          # 10 min
    CLASSICAL = "classical"  # 1 hour

# ═════════════════════════════════════════════════════════════════
# MODELS
# ═════════════════════════════════════════════════════════════════

class Player(Base):
    """Player model"""
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Ratings
    standard_rating = Column(Integer, default=1200)
    blitz_rating = Column(Integer, default=1200)
    rapid_rating = Column(Integer, default=1200)
    
    # Stats
    total_games = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    
    # Profile
    display_name = Column(String(100))
    avatar_url = Column(String(500))
    country = Column(String(50))
    
    # Account
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_online = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    white_games = relationship("Game", foreign_keys="Game.white_player_id", back_populates="white_player")
    black_games = relationship("Game", foreign_keys="Game.black_player_id", back_populates="black_player")
    rating_history = relationship("RatingHistory", back_populates="player")

class Game(Base):
    """Game model"""
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True)
    
    # Players
    white_player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    black_player_id = Column(Integer, ForeignKey("players.id"))
    
    # Game info
    status = Column(Enum(GameStatus), default=GameStatus.PENDING)
    result = Column(Enum(GameResult))
    time_control = Column(Enum(TimeControl), default=TimeControl.RAPID)
    
    # Game data
    fen = Column(Text)  # Current FEN position
    pgn = Column(Text)  # Full game PGN
    moves = Column(Text)  # Comma-separated moves
    
    # Time management
    white_time_remaining = Column(Integer)  # milliseconds
    black_time_remaining = Column(Integer)
    increment = Column(Integer, default=0)  # milliseconds per move
    
    # AI info
    ai_difficulty = Column(String(20))  # If playing vs AI
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    room_code = Column(String(10))  # For multiplayer
    
    # Relationships
    white_player = relationship("Player", foreign_keys=[white_player_id], back_populates="white_games")
    black_player = relationship("Player", foreign_keys=[black_player_id], back_populates="black_games")
    analysis = relationship("GameAnalysis", back_populates="game", uselist=False)

class GameAnalysis(Base):
    """Post-game analysis"""
    __tablename__ = "game_analysis"
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), unique=True)
    
    # Best moves
    best_moves = Column(Text)  # JSON list of best moves
    blunders = Column(Text)    # JSON list of blunder moves
    mistakes = Column(Text)    # JSON list of mistake moves
    
    # Evaluations
    evaluation_graph = Column(Text)  # JSON of position evaluations
    opening_name = Column(String(100))
    opening_eco = Column(String(10))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="analysis")

class RatingHistory(Base):
    """Player rating history"""
    __tablename__ = "rating_history"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"))
    
    time_control = Column(Enum(TimeControl))
    old_rating = Column(Integer)
    new_rating = Column(Integer)
    rating_change = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="rating_history")

class Room(Base):
    """Multiplayer room"""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    
    # Players
    creator_id = Column(Integer, ForeignKey("players.id"))
    white_player_id = Column(Integer, ForeignKey("players.id"))
    black_player_id = Column(Integer, ForeignKey("players.id"))
    
    # Settings
    time_control = Column(Enum(TimeControl), default=TimeControl.RAPID)
    is_private = Column(Boolean, default=False)
    
    # State
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    
    creator = relationship("Player", foreign_keys=[creator_id])

# ═════════════════════════════════════════════════════════════════
# DATABASE SESSION
# ═════════════════════════════════════════════════════════════════

def init_db(database_url: str = "sqlite:///./chess.db"):
    """Initialize database"""
    engine = create_engine(database_url, connect_args={"check_same_thread": False} if "sqlite" in database_url else {})
    Base.metadata.create_all(bind=engine)
    return engine

def get_session(engine):
    """Create database session"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
