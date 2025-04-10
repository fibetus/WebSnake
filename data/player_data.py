class PlayerData:
    def __init__(self):
        self.players = []  # List to store player names and scores

    def add_player(self, name, score=0):
        self.players.append({"name": name, "score": score})

    def get_players(self):
        return self.players

    def get_high_scores(self, limit=10):
        """Return top scores sorted by score descending"""
        sorted_players = sorted(self.players, key=lambda x: x["score"], reverse=True)
        return sorted_players[:limit]