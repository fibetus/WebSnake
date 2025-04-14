from typing import List, Dict, Any, Optional
from datetime import datetime
from bson.objectid import ObjectId


class Player:
    """Data model for a player."""

    def __init__(self, name: str, map_size: int, score: int = 0,
                 created_by: str = "user", created_at: datetime = None,
                 updated_at: datetime = None, id: str = None):
        self.id = id
        self.name = name
        self.map_size = map_size
        self.score = score
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for database storage."""
        data = {
            "name": self.name,
            "map_size": self.map_size,
            "score": self.score,
            "created_by": self.created_by,
            "created_at": self.created_at
        }

        # Only include updated_at if it exists
        if self.updated_at:
            data["updated_at"] = self.updated_at

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create Player instance from dictionary."""
        id_str = str(data.get("_id")) if data.get("_id") else None
        return cls(
            id=id_str,
            name=data.get("name"),
            map_size=data.get("map_size"),
            score=data.get("score"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class GameResult:
    """Data model for a game result."""

    def __init__(self, player_name: str, map_size: int, score: int,
                 duration: float, player_id=None, created_by: str = "user",
                 date: datetime = None, id: str = None):
        self.id = id
        self.player_name = player_name
        self.player_id = player_id
        self.map_size = map_size
        self.score = score
        self.duration = duration
        self.created_by = created_by
        self.date = date or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert game result to dictionary for database storage."""
        data = {
            "player_name": self.player_name,
            "map_size": self.map_size,
            "score": self.score,
            "duration": self.duration,
            "created_by": self.created_by,
            "date": self.date
        }

        # Only include player_id if it exists
        if self.player_id:
            if isinstance(self.player_id, str) and len(self.player_id) == 24:
                data["player_id"] = ObjectId(self.player_id)
            else:
                data["player_id"] = self.player_id

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameResult':
        """Create GameResult instance from dictionary."""
        id_str = str(data.get("_id")) if data.get("_id") else None
        player_id_str = str(data.get("player_id")) if data.get("player_id") else None

        return cls(
            id=id_str,
            player_name=data.get("player_name"),
            map_size=data.get("map_size"),
            score=data.get("score"),
            duration=data.get("duration"),
            player_id=player_id_str,
            created_by=data.get("created_by"),
            date=data.get("date")
        )