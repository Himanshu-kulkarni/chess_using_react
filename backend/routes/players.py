"""
Player endpoints
GET    /api/players/{username}
POST   /api/players/register
GET    /api/players/{username}/stats
GET    /api/players/{username}/games
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib

from models import Player, init_db, get_session, GameResult

router = APIRouter()

# ═════════════════════════════════════════════════════════════════
# SCHEMAS
# ═════════════════════════════════════════════════════════════════

class PlayerRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class PlayerResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    standard_rating: int
    blitz_rating: int
    rapid_rating: int
    total_games: int
    wins: int
    losses: int
    draws: int
    country: Optional[str]
    created_at: str

class PlayerStatsResponse(BaseModel):
    username: str
    total_games: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    standard_rating: int
    blitz_rating: int
    rapid_rating: int

# ═════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    """Get database session"""
    engine = init_db()
    return get_session(engine)

# ═════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@router.post("/register", response_model=PlayerResponse)
async def register_player(request: PlayerRegisterRequest):
    """Register new player"""
    db = get_db()
    
    # Check if username exists
    existing = db.query(Player).filter(Player.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing = db.query(Player).filter(Player.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new player
    player = Player(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
        display_name=request.display_name or request.username,
        standard_rating=1200,
        blitz_rating=1200,
        rapid_rating=1200,
    )
    
    db.add(player)
    db.commit()
    db.refresh(player)
    
    return PlayerResponse(
        id=player.id,
        username=player.username,
        display_name=player.display_name,
        standard_rating=player.standard_rating,
        blitz_rating=player.blitz_rating,
        rapid_rating=player.rapid_rating,
        total_games=player.total_games,
        wins=player.wins,
        losses=player.losses,
        draws=player.draws,
        country=player.country,
        created_at=player.created_at.isoformat(),
    )

@router.get("/{username}", response_model=PlayerResponse)
async def get_player(username: str):
    """Get player profile"""
    db = get_db()
    player = db.query(Player).filter(Player.username == username).first()
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return PlayerResponse(
        id=player.id,
        username=player.username,
        display_name=player.display_name,
        standard_rating=player.standard_rating,
        blitz_rating=player.blitz_rating,
        rapid_rating=player.rapid_rating,
        total_games=player.total_games,
        wins=player.wins,
        losses=player.losses,
        draws=player.draws,
        country=player.country,
        created_at=player.created_at.isoformat(),
    )

@router.get("/{username}/stats", response_model=PlayerStatsResponse)
async def get_player_stats(username: str):
    """Get player statistics"""
    db = get_db()
    player = db.query(Player).filter(Player.username == username).first()
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    win_rate = 0.0
    if player.total_games > 0:
        win_rate = player.wins / player.total_games
    
    return PlayerStatsResponse(
        username=player.username,
        total_games=player.total_games,
        wins=player.wins,
        losses=player.losses,
        draws=player.draws,
        win_rate=win_rate,
        standard_rating=player.standard_rating,
        blitz_rating=player.blitz_rating,
        rapid_rating=player.rapid_rating,
    )

@router.get("/")
async def list_players(limit: int = Query(100, le=1000)):
    """List top players"""
    db = get_db()
    players = db.query(Player).order_by(Player.standard_rating.desc()).limit(limit).all()
    
    return [
        {
            "username": p.username,
            "display_name": p.display_name,
            "rating": p.standard_rating,
            "total_games": p.total_games,
        }
        for p in players
    ]
