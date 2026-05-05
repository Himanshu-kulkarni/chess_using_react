"""
ELO rating system
"""
import math
from typing import Tuple

class ELOCalculator:
    """Calculate ELO rating changes"""
    
    K_FACTOR = 32  # Rating change factor
    MIN_RATING = 400
    MAX_RATING = 3000
    
    @staticmethod
    def calculate_expected_score(rating1: int, rating2: int) -> Tuple[float, float]:
        """
        Calculate expected scores for both players
        
        Args:
            rating1: Rating of player 1
            rating2: Rating of player 2
        
        Returns:
            (expected_score_1, expected_score_2)
        """
        diff = rating2 - rating1
        expected1 = 1.0 / (1.0 + 10 ** (diff / 400.0))
        expected2 = 1.0 - expected1
        
        return expected1, expected2
    
    @staticmethod
    def update_rating(player_rating: int, opponent_rating: int, 
                     result: float, k_factor: int = K_FACTOR) -> Tuple[int, int]:
        """
        Calculate new rating
        
        Args:
            player_rating: Player's current rating
            opponent_rating: Opponent's rating
            result: Game result (1.0 = win, 0.5 = draw, 0.0 = loss)
            k_factor: K-factor (higher = more volatile)
        
        Returns:
            (new_rating, rating_change)
        """
        expected, _ = ELOCalculator.calculate_expected_score(player_rating, opponent_rating)
        
        rating_change = k_factor * (result - expected)
        new_rating = player_rating + rating_change
        
        # Clamp rating
        new_rating = max(ELOCalculator.MIN_RATING, min(ELOCalculator.MAX_RATING, int(new_rating)))
        change = new_rating - player_rating
        
        return new_rating, change
    
    @staticmethod
    def process_game(white_rating: int, black_rating: int, 
                    result: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Process game result and calculate new ratings
        
        Args:
            white_rating: White player's rating
            black_rating: Black player's rating
            result: Game result ("white_win", "black_win", "draw")
        
        Returns:
            ((new_white_rating, white_change), (new_black_rating, black_change))
        """
        if result == "white_win":
            white_result = 1.0
            black_result = 0.0
        elif result == "black_win":
            white_result = 0.0
            black_result = 1.0
        else:  # draw
            white_result = 0.5
            black_result = 0.5
        
        new_white, white_change = ELOCalculator.update_rating(white_rating, black_rating, white_result)
        new_black, black_change = ELOCalculator.update_rating(black_rating, white_rating, black_result)
        
        return (new_white, white_change), (new_black, black_change)
    
    @staticmethod
    def get_rating_category(rating: int) -> str:
        """Get rating category/title"""
        if rating < 1000:
            return "Beginner"
        elif rating < 1400:
            return "Intermediate"
        elif rating < 1700:
            return "Advanced"
        elif rating < 2000:
            return "Expert"
        elif rating < 2200:
            return "Master"
        else:
            return "Grandmaster"
