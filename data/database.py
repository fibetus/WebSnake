from pymongo import MongoClient
from typing import List, Dict, Any, Optional
import datetime


class Database:
    """MongoDB Atlas database connection and operations."""

    def __init__(self):
        """Initialize the database connection."""
        self.client = None
        self.db = None
        self.players = None
        self.game_results = None
        self.is_connected = False

        # Store metadata about the current session
        self.metadata = {
            "user": "user",
            "session_start": "2025-04-11 12:48:12"
        }

    def connect(self) -> bool:
        """
        Connect to MongoDB Atlas.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient("mongodb+srv://user:passwordForUser@pythongame.oncdghw.mongodb.net/?retryWrites=true&w=majority&appName=PythonGame")
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




# Create a singleton instance
db = Database()