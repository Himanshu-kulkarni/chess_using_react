"""
Multiplayer endpoints
POST   /api/multiplayer/room/create
POST   /api/multiplayer/room/{code}/join
GET    /api/multiplayer/room/{code}/status
POST   /api/multiplayer/room/{code}/leave
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import string
import random

from models import game_manager, TimeControl, Room, init_db, get_session, Player

router = APIRouter()

# ═════════════════════════════════════════════════════════════════
# SCHEMAS
# ═════════════════════════════════════════════════════════════════

class CreateRoomRequest(BaseModel):
    creator: str
    time_control: TimeControl = TimeControl.RAPID
    is_private: bool = False

class JoinRoomRequest(BaseModel):
    player: str

class RoomResponse(BaseModel):
    code: str
    creator: str
    white_player: Optional[str]
    black_player: Optional[str]
    time_control: str
    is_active: bool

# ═════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════

def generate_room_code(length: int = 6) -> str:
    """Generate random room code"""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ═════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@router.post("/room/create", response_model=RoomResponse)
async def create_room(request: CreateRoomRequest):
    """Create multiplayer room"""
    db = get_session(init_db())
    
    # Verify creator exists
    creator = db.query(Player).filter(Player.username == request.creator).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Generate room code
    code = generate_room_code()
    
    # Create room in DB
    room = Room(
        code=code,
        creator_id=creator.id,
        white_player_id=creator.id,
        time_control=request.time_control,
        is_private=request.is_private,
    )
    
    db.add(room)
    db.commit()
    db.refresh(room)
    
    return RoomResponse(
        code=code,
        creator=request.creator,
        white_player=request.creator,
        black_player=None,
        time_control=request.time_control.value,
        is_active=True,
    )

@router.post("/room/{code}/join", response_model=RoomResponse)
async def join_room(code: str, request: JoinRoomRequest):
    """Join multiplayer room"""
    db = get_session(init_db())
    
    # Find room
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Verify player exists
    player = db.query(Player).filter(Player.username == request.player).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Check room status
    if not room.is_active:
        raise HTTPException(status_code=400, detail="Room is not active")
    
    if room.black_player_id:
        raise HTTPException(status_code=400, detail="Room is full")
    
    # Add player as black
    room.black_player_id = player.id
    db.commit()
    
    # Create game
    white_name = db.query(Player).filter(Player.id == room.white_player_id).first().username
    black_name = request.player
    
    game = game_manager.create_game(
        white_player=white_name,
        black_player=black_name,
        time_control=room.time_control,
    )
    
    return RoomResponse(
        code=code,
        creator=db.query(Player).filter(Player.id == room.creator_id).first().username,
        white_player=white_name,
        black_player=black_name,
        time_control=room.time_control.value,
        is_active=True,
    )

@router.get("/room/{code}/status", response_model=RoomResponse)
async def get_room_status(code: str):
    """Get room status"""
    db = get_session(init_db())
    
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    white = db.query(Player).filter(Player.id == room.white_player_id).first()
    black = db.query(Player).filter(Player.id == room.black_player_id).first() if room.black_player_id else None
    creator = db.query(Player).filter(Player.id == room.creator_id).first()
    
    return RoomResponse(
        code=code,
        creator=creator.username,
        white_player=white.username if white else None,
        black_player=black.username if black else None,
        time_control=room.time_control.value,
        is_active=room.is_active,
    )

@router.post("/room/{code}/leave")
async def leave_room(code: str, player: str = Query(...)):
    """Leave room"""
    db = get_session(init_db())
    
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Mark room as inactive
    room.is_active = False
    db.commit()
    
    return {"message": "Left room"}

@router.get("/rooms/public")
async def list_public_rooms(limit: int = Query(50, le=100)):
    """List public multiplayer rooms"""
    db = get_session(init_db())
    
    rooms = db.query(Room).filter(
        Room.is_private == False,
        Room.is_active == True,
        Room.black_player_id == None,
    ).limit(limit).all()
    
    result = []
    for room in rooms:
        white = db.query(Player).filter(Player.id == room.white_player_id).first()
        result.append({
            "code": room.code,
            "creator": white.username if white else "Unknown",
            "time_control": room.time_control.value,
            "players": "1/2",
        })
    
    return result
