"""
Game analysis endpoints
GET    /api/analysis/{game_id}
POST   /api/analysis/{game_id}/analyze
GET    /api/analysis/{game_id}/best-moves
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json

from models import game_manager, GameAnalysis, init_db, get_session
from engine import ChessEngine, FENParser, MoveGenerator

router = APIRouter()

# ═════════════════════════════════════════════════════════════════
# SCHEMAS
# ═════════════════════════════════════════════════════════════════

class AnalysisResponse(BaseModel):
    game_id: str
    best_moves: List[dict]
    blunders: List[dict]
    mistakes: List[dict]
    evaluation_graph: List[float]

class MoveAnalysis(BaseModel):
    move: str
    evaluation: float
    is_best: bool
    is_blunder: bool

# ═════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═════════════════════════════════════════════════════════════════

@router.post("/{game_id}/analyze")
async def analyze_game(game_id: str):
    """Analyze completed game"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if not game.is_finished:
        raise HTTPException(status_code=400, detail="Game not finished yet")
    
    # Analyze each position
    engine = ChessEngine()
    board = game.board.__class__()  # Start position
    board._init_standard()
    
    evaluations = []
    best_moves = []
    blunders = []
    mistakes = []
    
    for i, move in enumerate(game.move_history):
        # Get position evaluation
        eval_score = engine.search(board, max_depth=5, max_time=1.0)
        evaluations.append(eval_score if eval_score else 0)
        
        # Store move info
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
        
        if eval_score == best_moves and i < len(legal_moves):
            best_moves.append({"move": str(move), "number": i})
        
        # Make move
        MoveGenerator.make_move(board, move)
    
    analysis = {
        "game_id": game_id,
        "best_moves": best_moves,
        "blunders": blunders,
        "mistakes": mistakes,
        "evaluation_graph": evaluations,
    }
    
    return analysis

@router.get("/{game_id}/best-moves")
async def get_best_moves(game_id: str):
    """Get best moves for each position in game"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    engine = ChessEngine()
    board = game.board.__class__()
    board._init_standard()
    
    best_moves = []
    
    for i, move in enumerate(game.move_history):
        # Get best move for current position
        best = engine.search(board, max_depth=5, max_time=0.5)
        
        best_moves.append({
            "move_number": i + 1,
            "played_move": str(move),
            "best_move": str(best) if best else None,
            "is_best": str(move) == str(best) if best else False,
        })
        
        # Make move
        MoveGenerator.make_move(board, move)
    
    return {
        "game_id": game_id,
        "best_moves": best_moves,
    }

@router.get("/{game_id}")
async def get_analysis(game_id: str):
    """Get stored analysis for game"""
    db = get_session(init_db())
    
    analysis = db.query(GameAnalysis).filter(GameAnalysis.game_id == int(game_id)).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "game_id": game_id,
        "best_moves": json.loads(analysis.best_moves) if analysis.best_moves else [],
        "blunders": json.loads(analysis.blunders) if analysis.blunders else [],
        "mistakes": json.loads(analysis.mistakes) if analysis.mistakes else [],
        "opening": analysis.opening_name,
        "eco": analysis.opening_eco,
    }
