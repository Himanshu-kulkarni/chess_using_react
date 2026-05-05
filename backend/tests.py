"""
Integration tests for chess platform
"""
import pytest
from engine import Board, Color, PieceType, Move, MoveGenerator, ChessEngine, FENParser
from models import GameState, ELOCalculator, TimeControl

class TestChessEngine:
    """Test chess engine"""
    
    def test_initial_position(self):
        board = Board()
        legal_moves = MoveGenerator.generate_legal_moves(board, Color.WHITE)
        assert len(legal_moves) == 20  # 16 pawn moves + 4 knight moves
    
    def test_move_execution(self):
        board = Board()
        move = Move("e2", "e4")
        
        legal_moves = MoveGenerator.generate_legal_moves(board, Color.WHITE)
        assert move in legal_moves
        
        MoveGenerator.make_move(board, move)
        assert board.turn == Color.BLACK
        assert board.squares[28] == 0  # e2 now empty
        assert board.squares[20] != 0  # e4 now has piece
    
    def test_castling_rights(self):
        board = Board()
        assert board.castling["K"] and board.castling["Q"]
        assert board.castling["k"] and board.castling["q"]
    
    def test_fen_parsing(self):
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        board = FENParser.from_fen(fen)
        
        assert board.turn == Color.BLACK
        assert board.en_passant is not None
        assert FENParser.to_fen(board) == fen

class TestGameState:
    """Test game state management"""
    
    def test_create_game(self):
        game = GameState("game1", "alice", "bob", TimeControl.RAPID)
        
        assert game.game_id == "game1"
        assert game.white_player == "alice"
        assert game.black_player == "bob"
        assert game.is_active
        assert not game.is_finished
    
    def test_make_move(self):
        game = GameState("game1", "alice", "bob", TimeControl.RAPID)
        move = Move("e2", "e4")
        
        assert game.make_move(move, "alice")
        assert len(game.move_history) == 1
        assert game.board.turn == Color.BLACK
    
    def test_game_end_conditions(self):
        game = GameState("game1", "alice", "bob")
        
        # Simulate Scholar's mate
        moves_str = ["e2e4", "e7e5", "f1c4", "b8c6", "d1h5", "g8f6", "h5f7"]
        
        for move_str in moves_str:
            move = Move(move_str[:2], move_str[2:4])
            player = "alice" if len(game.move_history) % 2 == 0 else "bob"
            game.make_move(move, player)
        
        assert game.is_finished

class TestELO:
    """Test ELO rating system"""
    
    def test_rating_calculation(self):
        (white_new, white_change), (black_new, black_change) = ELOCalculator.process_game(
            1600, 1400, "white_win"
        )
        
        assert white_new > 1600
        assert black_new < 1400
        assert white_change + black_change == 0  # ELO is zero-sum
    
    def test_draw(self):
        (white_new, white_change), (black_new, black_change) = ELOCalculator.process_game(
            1600, 1400, "draw"
        )
        
        assert white_new < 1600  # Higher rated player loses rating in draw
        assert black_new > 1400  # Lower rated player gains rating in draw

class TestAIEngine:
    """Test AI search"""
    
    def test_ai_search(self):
        board = Board()
        engine = ChessEngine()
        
        move = engine.search(board, max_depth=3, max_time=1.0)
        
        assert move is not None
        assert isinstance(move, Move)
        
        # Verify it's a legal move
        legal_moves = MoveGenerator.generate_legal_moves(board, Color.WHITE)
        assert move in legal_moves
    
    def test_transposition_table(self):
        board = Board()
        engine = ChessEngine()
        
        engine.search(board, max_depth=5, max_time=2.0)
        
        assert engine.tt.get_size_mb() > 0
        assert engine.tt.get_hit_rate() >= 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
