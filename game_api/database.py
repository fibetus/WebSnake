import pymongo
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
            "user": "user",
            "session_start": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def connect(self) -> bool:
        """
        Connect to MongoDB Atlas and ensure indexes exist.

        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.is_connected:
            return True
        try:
            MONGO_URI = "mongodb+srv://user:passwordForUser@pythongame.oncdghw.mongodb.net/?retryWrites=true&w=majority&appName=PythonGame"
            self.client = MongoClient(MONGO_URI)
            self.client.admin.command('ping')

            self.db = self.client["user"]
            self.players = self.db["players"]
            self.game_results = self.db["game_results"]

            try:
                self.players.create_index([("name", 1), ("map_size", 1)], unique=True)
                print("Index created/verified for players: name_1_map_size_1")
            except pymongo.errors.OperationFailure as e:
                # Error code 85: IndexOptionsConflict (e.g., changing unique property)
                # Error code 86: IndexKeySpecsConflict (e.g., changing key definition for same name)
                if e.code in [85, 86]:
                     print(f"Warning: Index 'name_1_map_size_1' on players already exists with potentially different options. Details: {e.details}")
                else:
                    print(f"Warning: Could not create/verify index 'name_1_map_size_1' on players: {e}")

            try:
                self.game_results.create_index([("player_name", 1), ("date", -1)])
                print("Index created/verified for game_results: player_name_1_date_-1")
            except pymongo.errors.OperationFailure as e:
                 if e.code in [85, 86]:
                     print(f"Warning: Index 'player_name_1_date_-1' on game_results already exists. Details: {e.details}")
                 else:
                     print(f"Warning: Could not create/verify index 'player_name_1_date_-1' on game_results: {e}")

            try:
                self.game_results.create_index([("player_id", 1)])
                print("Index created/verified for game_results: player_id_1")
            except pymongo.errors.OperationFailure as e:
                 if e.code in [85, 86]:
                     print(f"Warning: Index 'player_id_1' on game_results already exists. Details: {e.details}")
                 else:
                     print(f"Warning: Could not create/verify index 'player_id_1' on game_results: {e}")


            self.is_connected = True
            print("Successfully connected to MongoDB Atlas (Indexes checked).")
            return True
        except pymongo.errors.ConfigurationError as e:
             print(f"MongoDB Atlas configuration error (check URI/credentials?): {e}")
             self.is_connected = False
             return False
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
            print("Disconnected from MongoDB Atlas")

    def _get_warsaw_time(self) -> datetime.datetime:
        """
        Get current time in Warsaw timezone (naive).
        """
        try:
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            warsaw_time = utc_now.astimezone(ZoneInfo("Europe/Warsaw"))
            return warsaw_time.replace(tzinfo=None)
        except Exception as e:
            print(f"Error getting Warsaw time: {e}. Falling back to UTC naive.")
            return datetime.datetime.utcnow()


    # Player CRUD operations
    def add_player(self, name: str, map_size: int, score: int = 0) -> Optional[ObjectId]:
        """
        Add a player if they don't exist for the given map size,
        or update their high score if the new score is better.

        Args:
            name (str): Player's name.
            map_size (int): Size of the game map.
            score (int): Score to potentially update (used by add_game_result).

        Returns:
            Optional[ObjectId]: The ObjectId of the player record, or None if failed.
        """
        if not self.is_connected and not self.connect():
            print("Error: Cannot add player, DB not connected.")
            return None

        try:
            result = self.players.update_one(
                {"name": name, "map_size": map_size},
                {
                    "$setOnInsert": {
                        "name": name,
                        "map_size": map_size,
                        "created_by": self.metadata["user"],
                        "created_at": self._get_warsaw_time()
                    },
                    "$max": {"score": score},
                    "$set": {"updated_at": self._get_warsaw_time()}
                },
                upsert=True # Create the document if it doesn't exist
            )

            if result.upserted_id:
                print(f"Player '{name}' created for map size {map_size} with score {score}.")
                return result.upserted_id
            elif result.matched_count > 0:
                 player_doc = self.players.find_one({"name": name, "map_size": map_size})
                 if player_doc:
                     print(f"Player '{name}' score updated/checked for map size {map_size}.")
                     return player_doc["_id"]
                 else:
                      print(f"Warning: Player '{name}' matched but couldn't be found after update.")
                      return None
            else:
                print(f"Warning: Player '{name}' update/upsert failed unexpectedly.")
                return None

        except Exception as e:
            print(f"Error adding/updating player '{name}': {e}")
            return None

    def get_players(self) -> List[Player]:
        if not self.is_connected and not self.connect(): return []
        try:
            players_data = list(self.players.find())
            return [Player.from_dict(p) for p in players_data]
        except Exception as e:
            print(f"Error getting players: {e}"); return []

    def get_high_scores(self, limit: int = 10, map_size: Optional[int] = None) -> List[Player]:
        if not self.is_connected and not self.connect(): return []
        try:
            query = {} if map_size is None else {"map_size": map_size}
            top_players_data = list(self.players.find(query).sort("score", -1).limit(limit))
            return [Player.from_dict(p) for p in top_players_data]
        except Exception as e:
            print(f"Error getting high scores: {e}"); return []

    def update_player(self, name: str, map_size: int, score: int) -> bool:
        if not self.is_connected and not self.connect(): return False
        try:
            result = self.players.update_one(
                {"name": name, "map_size": map_size, "score": {"$lt": score}}, # Only update if new score is higher
                {
                    "$set": {"score": score, "updated_at": self._get_warsaw_time()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating player: {e}"); return False

    def delete_player(self, name: str, map_size: Optional[int] = None) -> bool:
        if not self.is_connected and not self.connect(): return False
        try:
            query = {"name": name}
            if map_size is not None: query["map_size"] = map_size
            result = self.players.delete_many(query)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting player: {e}"); return False


    def add_game_result(self, player_name: str, map_size: int, score: int, duration: float) -> Optional[ObjectId]:
        """
        Add a game result and update the player's high score for that map size.

        Args:
            player_name (str): Player's name.
            map_size (int): Size of the game map.
            score (int): Score achieved in the game.
            duration (float): Game duration in seconds.

        Returns:
            Optional[ObjectId]: The ObjectId of the added game result, or None if failed.
        """
        if not self.is_connected and not self.connect():
            print("Error: Cannot add game result, DB not connected.")
            return None

        try:
            player_id = self.add_player(name=player_name, map_size=map_size, score=score)

            if not player_id:
                print(f"Error: Failed to get/create player '{player_name}' for game result.")
                return None

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
            print(f"Game result added for '{player_name}' with score {score}.")
            return result.inserted_id

        except Exception as e:
            print(f"Error adding game result for '{player_name}': {e}")
            return None

    def get_player_results(self, player_name: str, map_size: Optional[int] = None) -> List[GameResult]:
        """
        Get all game results for a player, optionally filtered by map size.
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
            print(f"Error getting player results for '{player_name}': {e}")
            return []


# Create a singleton instance
db = Database()
