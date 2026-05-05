"""
Validation utilities
"""
from engine import Move, MoveGenerator, Board

def validate_move(move_str: str, board: Board) -> bool:
    """Validate move format and legality"""
    try:
        if len(move_str) < 4:
            return False
        
        from_sq = move_str[:2]
        to_sq = move_str[2:4]
        
        # Check valid algebraic notation
        if not (from_sq[0] in 'abcdefgh' and from_sq[1] in '12345678' and
                to_sq[0] in 'abcdefgh' and to_sq[1] in '12345678'):
            return False
        
        # Check move is legal
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
        move = Move(from_sq, to_sq)
        
        return move in legal_moves
    except:
        return False

def validate_game_state(game_state: dict) -> bool:
    """Validate game state structure"""
    required_fields = ['game_id', 'fen', 'white_time', 'black_time', 'current_turn']
    return all(field in game_state for field in required_fields)
