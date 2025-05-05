from typing import List, Dict, Any, Optional
import time
from game_api.database import db


class PlayerData:
    """
    Player data manager using MongoDB Atlas backend.
    """

    def __init__(self):
        """
        Initialize the player data manager and connect to MongoDB Atlas.
        """
        # Connect to the database
        self.connected = db.connect()
        self.players = []
        self.game_start_time = 0

    def add_player(self, name: str, score: int = 0, map_size: int = None):
        """
        Add a player with optional initial score.

        Args:
            name: Player's name
            score: Initial score (default: 0)
            map_size: Size of the game map (default: None, will be set when game starts)
        """
        if map_size is None:
            self.players.append({"name": name, "score": score})
            return

        # Add to database when map_size is available
        db.add_player(name, map_size, score)

        # Update the local cache as well
        for player in self.players:
            if player["name"] == name:
                player["score"] = max(player["score"], score)
                return

        # If not found, add to local cache
        self.players.append({"name": name, "score": score, "map_size": map_size})

    def get_players(self) -> List[Dict[str, Any]]:
        """
        Get all players.

        Returns:
            List of player dictionaries with 'name' and 'score' keys
        """
        # Try to get from database
        if self.connected:
            db_players = db.get_players()
            # Convert Player objects to simple format for compatibility
            self.players = [{"name": p.name, "score": p.score} for p in db_players]

        return self.players

    def get_high_scores(self, limit: int = 10, map_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Return top scores sorted by score descending.

        Args:
            limit: Maximum number of scores to return
            map_size: If provided, filter scores by this map size

        Returns:
            List of player dictionaries with 'name', 'score', and 'map_size' keys
        """
        if self.connected:
            # Get from database
            db_players = db.get_high_scores(limit, map_size)
            # Ensure map_size is included in returned data
            return [{"name": p.name, "score": p.score, "map_size": p.map_size} for p in db_players]
        else:
            # Sort locally
            sorted_players = sorted(self.players, key=lambda x: x["score"], reverse=True)
            # Filter by map_size if specified
            if map_size is not None:
                sorted_players = [p for p in sorted_players if p.get("map_size") == map_size]
            return sorted_players[:limit]

    def update_player_score(self, name: str, score: int, map_size: Optional[int] = None) -> bool:
        """
        Update a player's score.

        Args:
            name: Player's name
            score: New score
            map_size: Size of the game map

        Returns:
            bool: True if successful, False otherwise
        """
        # Update database if map_size is available
        if self.connected and map_size is not None:
            db.update_player(name, map_size, score)

        # Update local cache as well
        for player in self.players:
            if player["name"] == name:
                player["score"] = max(player["score"], score)
                return True

        # If player wasn't found in local cache
        self.players.append({"name": name, "score": score})
        return True

    def start_game_timer(self):
        """
        Start timing a game session.
        """
        self.game_start_time = time.time()

    def save_game_result(self, name: str, score: int, map_size: int) -> bool:
        """
        Save a game result.

        Args:
            name: Player's name
            score: Score achieved
            map_size: Size of the game map

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            return False

        # Calculate duration
        duration = time.time() - self.game_start_time if self.game_start_time > 0 else 0

        # Reset timer
        self.game_start_time = 0

        return db.add_game_result(name, map_size, score, duration) is not None

    def get_player_history(self, name: str, map_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get a player's game history.

        Args:
            name: Player's name
            map_size: If provided, filter results by this map size

        Returns:
            List of game result dictionaries
        """
        if not self.connected:
            return []

        game_results = db.get_player_results(name, map_size)
        # Convert GameResult objects to dictionaries
        return [
            {
                "player_name": result.player_name,
                "map_size": result.map_size,
                "score": result.score,
                "duration": result.duration,
                "date": result.date
            }
            for result in game_results
        ]