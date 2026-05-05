"""
Game endpoints
GET  /api/games/{game_id}
POST /api/games/create
POST /api/games/{game_id}/move
POST /api/games/{game_id}/resign
GET  /api/games/{game_id}/status
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from models import game_manager, TimeControl, GameResult
from engine import Move, FENParser, PieceType

router = APIRouter()

# ═════════════════════════════════════════════════════════════════
# SCHEMAS
# ═════════════════════════════════════════════════════════════════

class CreateGameRequest(BaseModel):
    white_player: str
    black_player: Optional[str] = None
    time_control: TimeControl = TimeControl.RAPID
    ai_difficulty: Optional[str] = None

class MoveRequest(BaseModel):
    from_square: str  # e.g., "e2"
    to_square: str    # e.g., "e4"
    promotion: Optional[str] = None  # e.g., "queen"
    player: str

class GameResponse(BaseModel):
    game_id: str
    white_player: str
    black_player: str
    fen: str
    moves: list
    white_time: int
    black_time: int
    is_finished: bool
    result: Optional[str]
    current_turn: str

# ═════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@router.post("/create", response_model=GameResponse)
async def create_game(request: CreateGameRequest):
    """Create a new game"""
    game = game_manager.create_game(
        white_player=request.white_player,
        black_player=request.black_player,
        time_control=request.time_control,
        ai_difficulty=request.ai_difficulty,
    )
    
    return game.to_dict()

@router.get("/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    """Get game state"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game.to_dict()

@router.post("/{game_id}/move")
async def make_move(game_id: str, request: MoveRequest):
    """Make a move in game"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.is_finished:
        raise HTTPException(status_code=400, detail="Game is already finished")
    
    # Parse promotion
    promotion = None
    if request.promotion:
        promotion_map = {
            "queen": PieceType.QUEEN,
            "rook": PieceType.ROOK,
            "bishop": PieceType.BISHOP,
            "knight": PieceType.KNIGHT,
        }
        promotion = promotion_map.get(request.promotion.lower())
    
    # Create move object
    move = Move(request.from_square, request.to_square, promotion)
    
    # Make move
    if not game.make_move(move, request.player):
        raise HTTPException(status_code=400, detail="Invalid move")
    
    # If AI's turn and black is AI, make AI move
    if game.board.turn.value == 1 and game.black_player == "AI" and not game.is_finished:
        ai_move = game.get_ai_move()
        if ai_move:
            game.make_move(ai_move, "AI")
    
    return game.to_dict()

@router.post("/{game_id}/resign")
async def resign_game(game_id: str, player: str = Query(...)):
    """Player resigns"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game.resign(player)
    return game.to_dict()

@router.post("/{game_id}/draw")
async def offer_draw(game_id: str):
    """Offer draw"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if not game.offer_draw():
        raise HTTPException(status_code=400, detail="Cannot offer draw")
    
    return {"message": "Draw offered"}

@router.post("/{game_id}/undo")
async def undo_move(game_id: str):
    """Undo last move"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if not game.undo_move():
        raise HTTPException(status_code=400, detail="Cannot undo move")
    
    return game.to_dict()

@router.get("/{game_id}/legal-moves")
async def get_legal_moves(game_id: str):
    """Get legal moves for current position"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    legal_moves = game.get_legal_moves()
    return {
        "legal_moves": [str(m) for m in legal_moves],
        "count": len(legal_moves),
    }

@router.get("/{game_id}/status")
async def get_game_status(game_id: str):
    """Get game status"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {
        "game_id": game.game_id,
        "is_finished": game.is_finished,
        "result": game.result.value if game.result else None,
        "white_time": game.white_time,
        "black_time": game.black_time,
        "move_count": len(game.move_history),
    }
