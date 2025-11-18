import json
import os

class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()

        # High score should never be reset.
        self.high_score = self.load_high_score()

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        
    def load_high_score(self):
        """Load the high score from a file."""
        try:
            with open('high_score.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return 0
        except json.JSONDecodeError:
            return 0
            
    def save_high_score(self):
        """Save the high score to a file."""
        with open('high_score.json', 'w') as f:
            json.dump(self.high_score, f)