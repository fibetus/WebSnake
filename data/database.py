from pymongo import MongoClient
from typing import List, Optional
import datetime
from zoneinfo import ZoneInfo
from bson.objectid import ObjectId
from .models import Player, GameResult


class Database:
    """
    MongoDB Atlas database connection and operations.
    """

    def __init__(self):
        """
        Initialize the database connection.
        """
        self.client = None
        self.db = None
        self.players = None
        self.game_results = None
        self.is_connected = False

        # Store metadata about the current session
        self.metadata = {
            "user": "user",  # Updated with current user login
            "session_start": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def connect(self) -> bool:
        """
        Connect to MongoDB Atlas.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(
                "mongodb+srv://user:passwordForUser@pythongame.oncdghw.mongodb.net/?retryWrites=true&w=majority&appName=PythonGame")
            # Ping the server to verify connection
            self.client.admin.command('ping')

            self.db = self.client["user"]
            self.players = self.db["players"]
            self.game_results = self.db["game_results"]

            # Create indexes for better performance
            self.players.create_index([("name", 1), ("map_size", 1)])
            self.game_results.create_index([("player_name", 1), ("date", -1)])

            self.is_connected = True
            print("Successfully connected to MongoDB Atlas")
            return True
        except Exception as e:
            print(f"MongoDB Atlas connection error: {e}")
            self.is_connected = False
            return False

    def disconnect(self) -> None:
        """
        Close the database connection.
        """
        if self.client:
            self.client.close()
            self.is_connected = False

    def _get_warsaw_time(self) -> datetime.datetime:
        """
        Get current time in Warsaw timezone.

        Returns:
            datetime.datetime: Current time in Warsaw timezone
        """
        # Get current UTC time with timezone information
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        # Convert to Warsaw time
        warsaw_time = utc_now.astimezone(ZoneInfo("Europe/Warsaw"))
        # For MongoDB compatibility, remove timezone info but keep Warsaw time
        return warsaw_time.replace(tzinfo=None)

    # Player CRUD operations
    def add_player(self, name: str, map_size: int, score: int = 0) -> Optional[str]:
        """
        Add a player to the database or update if exists.

        Args:
            name: Player's name
            map_size: Size of the game map
            score: Initial score (default: 0)

        Returns:
            str: ID of the added player or None if failed
        """
        if not self.is_connected and not self.connect():
            return None

        try:
            # Check if player already exists with same name and map size
            existing = self.players.find_one({"name": name, "map_size": map_size})

            if existing:
                # Update the existing player if the new score is higher
                if score > existing.get("score", 0):
                    existing_player = Player.from_dict(existing)
                    existing_player.score = score
                    existing_player.updated_at = self._get_warsaw_time()

                    self.players.update_one(
                        {"_id": ObjectId(existing_player.id)},
                        {
                            "$set": {"score": score, "updated_at": existing_player.updated_at}
                        }
                    )
                return existing.get("_id")

            # Create new player model
            player = Player(
                name=name,
                map_size=map_size,
                score=score,
                created_by=self.metadata["user"],
                created_at=self._get_warsaw_time()
            )

            # Insert new player
            result = self.players.insert_one(player.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding player: {e}")
            return None

    def get_players(self) -> List[Player]:
        """
        Get all players from the database.

        Returns:
            List[Player]: List of Player objects
        """
        if not self.is_connected and not self.connect():
            return []

        try:
            players_data = list(self.players.find())
            return [Player.from_dict(player_data) for player_data in players_data]
        except Exception as e:
            print(f"Error getting players: {e}")
            return []

    def get_high_scores(self, limit: int = 10, map_size: Optional[int] = None) -> List[Player]:
        """
        Get top players by score, optionally filtered by map size.

        Args:
            limit: Maximum number of players to return
            map_size: If provided, filter scores by this map size

        Returns:
            List[Player]: List of top players sorted by score
        """
        if not self.is_connected and not self.connect():
            return []

        try:
            # Filter by map size if provided
            query = {"map_size": map_size} if map_size is not None else {}

            top_players_data = list(self.players.find(query).sort("score", -1).limit(limit))
            return [Player.from_dict(player_data) for player_data in top_players_data]
        except Exception as e:
            print(f"Error getting high scores: {e}")
            return []

    def update_player(self, name: str, map_size: int, score: int) -> bool:
        """
        Update a player's score.

        Args:
            name: Player's name
            map_size: Size of the game map
            score: New score

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected and not self.connect():
            return False

        try:
            # Only update if the new score is higher than the existing one
            result = self.players.update_one(
                {"name": name, "map_size": map_size, "score": {"$lt": score}},
                {
                    "$set": {"score": score},
                    "$currentDate": {"updated_at": True}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating player: {e}")
            return False

    def delete_player(self, name: str, map_size: Optional[int] = None) -> bool:
        """
        Delete a player from the database.

        Args:
            name: Player's name
            map_size: If provided, delete only entries with this map size

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected and not self.connect():
            return False

        try:
            query = {"name": name}
            if map_size is not None:
                query["map_size"] = map_size

            result = self.players.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting player: {e}")
            return False

    # Game results CRUD operations
    def add_game_result(self, player_name: str, map_size: int, score: int, duration: float) -> Optional[str]:
        """
        Add a game result to the database.

        Args:
            player_name: Player's name
            map_size: Size of the game map
            score: Score achieved in the game
            duration: Game duration in seconds

        Returns:
            str: ID of the added result or None if failed
        """
        if not self.is_connected and not self.connect():
            return None

        try:
            # Get or create player
            player = self.players.find_one({"name": player_name, "map_size": map_size})
            player_id = None

            if player:
                player_id = player["_id"]
                # Update player's score if higher
                if score > player.get("score", 0):
                    self.players.update_one(
                        {"_id": player_id},
                        {
                            "$set": {"score": score},
                            "$currentDate": {"updated_at": True}
                        }
                    )
            else:
                # Create new player
                new_player = Player(
                    name=player_name,
                    map_size=map_size,
                    score=score,
                    created_by=self.metadata["user"],
                    created_at=self._get_warsaw_time()
                )
                insert_result = self.players.insert_one(new_player.to_dict())
                player_id = insert_result.inserted_id

            # Create game result
            game_result = GameResult(
                player_name=player_name,
                map_size=map_size,
                score=score,
                duration=duration,
                player_id=player_id,
                created_by=self.metadata["user"],
                date=self._get_warsaw_time()
            )

            result = self.game_results.insert_one(game_result.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding game result: {e}")
            return None

    def get_player_results(self, player_name: str, map_size: Optional[int] = None) -> List[GameResult]:
        """
        Get all game results for a player.

        Args:
            player_name: Player's name
            map_size: If provided, filter results by this map size

        Returns:
            List[GameResult]: List of game results for the player
        """
        if not self.is_connected and not self.connect():
            return []

        try:
            query = {"player_name": player_name}
            if map_size is not None:
                query["map_size"] = map_size

            results_data = list(self.game_results.find(query).sort("date", -1))
            return [GameResult.from_dict(result_data) for result_data in results_data]
        except Exception as e:
            print(f"Error getting player results: {e}")
            return []


# Create a singleton instance
db = Database()