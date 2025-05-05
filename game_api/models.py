from typing import List, Dict, Any, Optional
from datetime import datetime
from bson.objectid import ObjectId


class Player:
    """
    Data model for a player.
    """

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
        """
        Convert player to dictionary for database storage.
        """
        data = {
            "name": self.name,
            "map_size": self.map_size,
            "score": self.score,
            "created_by": self.created_by,
            "created_at": self.created_at
        }
        if self.updated_at:
            data["updated_at"] = self.updated_at
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """
        Create Player instance from dictionary (retrieved from DB).
        """
        return cls(
            id=str(data.get("_id")) if data.get("_id") else None,
            name=data.get("name"),
            map_size=data.get("map_size"),
            score=data.get("score"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class GameResult:
    """
    Data model for a game result.
    """
    def __init__(self, player_name: str, map_size: int, score: int,
                 duration: float, player_id=None, created_by: str = "user",
                 date: datetime = None, id: str = None):
        self.id = id
        self.player_name = player_name

        # if isinstance(player_id, str) and len(player_id) == 24:
        #      try:
        #          self.player_id = ObjectId(player_id)
        #      except:
        #          self.player_id = None
        # elif isinstance(player_id, ObjectId):
        #      self.player_id = player_id
        # else:
        #     self.player_id = None
        ### Keeping the code, so if I need it later


        self.player_id = player_id
        self.map_size = map_size
        self.score = score
        self.duration = duration
        self.created_by = created_by
        self.date = date if date is not None else datetime.now()


    def to_dict(self) -> Dict[str, Any]:
        """
        Convert game result to dictionary for database storage.
        """
        data = {
            "player_name": self.player_name,
            "map_size": self.map_size,
            "score": self.score,
            "duration": self.duration,
            "created_by": self.created_by,
            "date": self.date
        }
        if self.player_id:
            data["player_id"] = self.player_id
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameResult':
        """
        Create GameResult instance from dictionary (retrieved from DB).
        """

        player_id_value = data.get("player_id")
        print(f"DEBUG: Got player_id_value: {repr(player_id_value)} (Type: {type(player_id_value)})")  # DEBUG PRINT 2

        is_oid = isinstance(player_id_value, ObjectId)
        print(f"DEBUG: Is player_id_value an ObjectId? {is_oid}")  # DEBUG PRINT 3

        final_player_id = str(player_id_value) if is_oid else player_id_value
        print(
            f"DEBUG: Final player_id to be used: {repr(final_player_id)} (Type: {type(final_player_id)})")  # DEBUG PRINT 4
        return cls(
            id=str(data.get("_id")) if data.get("_id") else None,
            player_name=data.get("player_name"),
            map_size=data.get("map_size"),
            score=data.get("score"),
            duration=data.get("duration"),
            player_id=str(player_id_value) if isinstance(player_id_value, ObjectId) else player_id_value,
            created_by=data.get("created_by"),
            date=data.get("date")
        )