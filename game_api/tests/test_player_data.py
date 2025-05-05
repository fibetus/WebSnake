import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from snake_project.game_api.data.models import Player, GameResult
from snake_project.game_api.data.database import db
from snake_project.game_api.data.player_data import PlayerData


@pytest.fixture
def mock_db():
    """
    Setup mock database instance with controlled responses
    """
    # Save original methods to restore later
    original_connect = db.connect
    original_add_player = db.add_player
    original_get_players = db.get_players
    original_get_high_scores = db.get_high_scores
    original_update_player = db.update_player
    original_add_game_result = db.add_game_result
    original_get_player_results = db.get_player_results

    # Create Player test objects
    player1 = Player("TestPlayer1", 10, 100)
    player1.id = "player1_id"
    player2 = Player("TestPlayer2", 10, 200)
    player2.id = "player2_id"
    player3 = Player("TestPlayer3", 15, 300)
    player3.id = "player3_id"

    # Create GameResult test objects
    game_result1 = GameResult("TestPlayer1", 10, 100, 60.5)
    game_result1.id = "result1_id"
    game_result1.date = datetime(2025, 4, 14, 12, 0, 0)

    game_result2 = GameResult("TestPlayer1", 10, 150, 75.0)
    game_result2.id = "result2_id"
    game_result2.date = datetime(2025, 4, 14, 13, 0, 0)

    # Set metadata with the current values
    db.metadata = {
        "user": "user",  # Using current user's login
        "session_start": "2025-04-14 14:17:59"  # Using current timestamp
    }

    # Setup mock methods
    db.connect = MagicMock(return_value=True)
    db.add_player = MagicMock(return_value="mock_player_id")
    db.get_players = MagicMock(return_value=[player1, player2, player3])
    db.get_high_scores = MagicMock(return_value=[player3, player2, player1])
    db.update_player = MagicMock(return_value=True)
    db.add_game_result = MagicMock(return_value="mock_result_id")
    db.get_player_results = MagicMock(return_value=[game_result1, game_result2])

    yield db

    # Restore original methods
    db.connect = original_connect
    db.add_player = original_add_player
    db.get_players = original_get_players
    db.get_high_scores = original_get_high_scores
    db.update_player = original_update_player
    db.add_game_result = original_add_game_result
    db.get_player_results = original_get_player_results


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """
    Clean up after each test
    """
    yield  # This runs the test
    # Reset any local state that might affect other tests
    if hasattr(db, '_instance'):
        db._instance = None


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_all_tests():
    """
    Global cleanup after all tests have completed
    """
    yield  # Let all tests run

    # Clean up real database if any test accidentally connected to it
    try:
        # Try to get a real connection and clean up test data
        from snake_project.game_api.data.database import Database
        cleanup_db = Database()
        if cleanup_db.connect():
            print("Cleaning up any test data from real database...")

            # Delete all test data created by our test user
            if cleanup_db.players is not None:
                cleanup_db.players.delete_many({
                    "$or": [
                        {"name": {"$regex": "^Test"}},
                        {"name": {"$in": ["TestPlayer1", "TestPlayer2", "TestPlayer3",
                                          "LocalPlayer", "DbPlayer", "ExistingPlayer"]}},
                        {"created_by": "fibetus"}  # Delete test data created by our test user
                    ]
                })

            if cleanup_db.game_results is not None:
                cleanup_db.game_results.delete_many({
                    "$or": [
                        {"player_name": {"$regex": "^Test"}},
                        {"player_name": {"$in": ["TestPlayer1", "TestPlayer2", "TestPlayer3",
                                                 "LocalPlayer", "DbPlayer", "ExistingPlayer"]}},
                        {"created_by": "fibetus"}  # Delete test data created by our test user
                    ]
                })

            cleanup_db.disconnect()
            print("Test data cleanup complete.")
    except Exception as e:
        print(f"Warning: Could not clean up test data: {e}")


class TestPlayerData:
    """
    Tests for PlayerData class
    """

    def test_init_connected(self, mock_db):
        """
        Test initialization when database connects successfully
        """
        player_data = PlayerData()
        assert player_data.connected is True
        assert player_data.players == []
        assert player_data.game_start_time == 0
        mock_db.connect.assert_called_once()

    def test_init_disconnected(self, mock_db):
        """
        Test initialization when database connection fails
        """
        mock_db.connect.return_value = False
        player_data = PlayerData()
        assert player_data.connected is False
        assert player_data.players == []
        assert player_data.game_start_time == 0
        mock_db.connect.assert_called_once()

    def test_add_player_local_only(self, mock_db):
        """
        Test adding a player locally (without map_size)
        """
        player_data = PlayerData()
        player_data.add_player("LocalPlayer", 150)

        # Should not call database method
        mock_db.add_player.assert_not_called()

        # Should add to local cache
        assert len(player_data.players) == 1
        assert player_data.players[0]["name"] == "LocalPlayer"
        assert player_data.players[0]["score"] == 150
        assert "map_size" not in player_data.players[0]

    def test_add_player_with_database(self, mock_db):
        """
        Test adding a player with map_size (database + local)
        """
        player_data = PlayerData()
        player_data.add_player("DbPlayer", 200, 10)

        # Should call database method
        mock_db.add_player.assert_called_once_with("DbPlayer", 10, 200)

        # Should add to local cache
        assert len(player_data.players) == 1
        assert player_data.players[0]["name"] == "DbPlayer"
        assert player_data.players[0]["score"] == 200
        assert player_data.players[0]["map_size"] == 10

    def test_add_player_existing_in_local_cache(self, mock_db):
        """
        Test adding a player that already exists in local cache
        """
        player_data = PlayerData()
        # Add first time
        player_data.add_player("ExistingPlayer", 100, 10)

        # Add again with higher score
        player_data.add_player("ExistingPlayer", 150, 10)

        # Should call database method twice
        assert mock_db.add_player.call_count == 2

        # Should update local cache without duplicating
        assert len(player_data.players) == 1
        assert player_data.players[0]["name"] == "ExistingPlayer"
        assert player_data.players[0]["score"] == 150  # Max score

        # Add again with lower score
        player_data.add_player("ExistingPlayer", 50, 10)

        # Should keep the higher score
        assert player_data.players[0]["score"] == 150

    def test_get_players_connected(self, mock_db):
        """
        Test getting players when connected to database
        """
        player_data = PlayerData()
        result = player_data.get_players()

        # Should call database method
        mock_db.get_players.assert_called_once()

        # Should update local cache with db results
        assert len(player_data.players) == 3

        # Verify returned data
        assert len(result) == 3
        # Confirm structure of returned data
        assert all(isinstance(p, dict) for p in result)
        assert all("name" in p and "score" in p for p in result)
        # Check specific values
        assert any(p["name"] == "TestPlayer1" and p["score"] == 100 for p in result)
        assert any(p["name"] == "TestPlayer2" and p["score"] == 200 for p in result)
        assert any(p["name"] == "TestPlayer3" and p["score"] == 300 for p in result)

    def test_get_players_disconnected(self, mock_db):
        """
        Test getting players when disconnected from database
        """
        mock_db.connect.return_value = False
        player_data = PlayerData()

        # Add some players locally
        player_data.add_player("LocalPlayer1", 100)
        player_data.add_player("LocalPlayer2", 200)

        result = player_data.get_players()

        # Should not call database method
        mock_db.get_players.assert_not_called()

        # Should return local cache
        assert len(result) == 2
        assert any(p["name"] == "LocalPlayer1" and p["score"] == 100 for p in result)
        assert any(p["name"] == "LocalPlayer2" and p["score"] == 200 for p in result)

    def test_get_high_scores_connected(self, mock_db):
        """
        Test getting high scores when connected to database
        """
        player_data = PlayerData()
        result = player_data.get_high_scores(limit=2)

        # Should call database method
        mock_db.get_high_scores.assert_called_once_with(2, None)

        # Verify returned data
        assert len(result) == 3  # Return all 3 since our mock returns 3
        # Confirm structure of returned data
        assert all(isinstance(p, dict) for p in result)
        assert all(key in p for p in result for key in ["name", "score", "map_size"])
        # Check order (sorted by score)
        assert result[0]["score"] >= result[1]["score"] >= result[2]["score"]

    def test_get_high_scores_with_map_size(self, mock_db):
        """
        Test getting high scores filtered by map size
        """
        player_data = PlayerData()
        # Set up mock to return filtered results
        filtered_players = [
            Player("TestPlayer1", 10, 100),
            Player("TestPlayer2", 10, 200)
        ]
        mock_db.get_high_scores.return_value = filtered_players

        result = player_data.get_high_scores(map_size=10)

        # Should call database method with filter
        mock_db.get_high_scores.assert_called_once_with(10, 10)

        # Verify returned data
        assert len(result) == 2
        assert all(p["map_size"] == 10 for p in result)

    def test_get_high_scores_disconnected(self, mock_db):
        """
        Test getting high scores when disconnected from database
        """
        mock_db.connect.return_value = False
        player_data = PlayerData()

        # Add some players locally with different scores and map sizes
        player_data.players = [
            {"name": "LocalPlayer1", "score": 100, "map_size": 10},
            {"name": "LocalPlayer2", "score": 300, "map_size": 10},
            {"name": "LocalPlayer3", "score": 200, "map_size": 15}
        ]

        # Test without map_size filter
        result = player_data.get_high_scores(limit=2)

        # Should not call database method
        mock_db.get_high_scores.assert_not_called()

        # Should return sorted local cache with limit
        assert len(result) == 2
        assert result[0]["name"] == "LocalPlayer2"  # Highest score
        assert result[1]["name"] == "LocalPlayer3"  # Second highest

        # Test with map_size filter
        result = player_data.get_high_scores(map_size=10)
        assert len(result) == 2
        assert all(p["map_size"] == 10 for p in result)
        assert result[0]["name"] == "LocalPlayer2"  # Highest score for map_size 10

    def test_update_player_score_connected_with_map_size(self, mock_db):
        """
        Test updating player score when connected with map_size
        """
        player_data = PlayerData()
        result = player_data.update_player_score("TestPlayer", 250, 10)

        # Should call database method
        mock_db.update_player.assert_called_once_with("TestPlayer", 10, 250)

        # Should add to local cache
        assert len(player_data.players) == 1
        assert player_data.players[0]["name"] == "TestPlayer"
        assert player_data.players[0]["score"] == 250

        # Should return success
        assert result is True

    def test_update_player_score_connected_without_map_size(self, mock_db):
        """
        Test updating player score when connected without map_size
        """
        player_data = PlayerData()
        result = player_data.update_player_score("TestPlayer", 250)

        # Should not call database method
        mock_db.update_player.assert_not_called()

        # Should add to local cache only
        assert len(player_data.players) == 1
        assert player_data.players[0]["name"] == "TestPlayer"
        assert player_data.players[0]["score"] == 250

        # Should return success
        assert result is True

    def test_update_player_score_existing_player(self, mock_db):
        """
        Test updating score for existing player in local cache
        """
        player_data = PlayerData()
        # Add player to local cache
        player_data.players = [{"name": "ExistingPlayer", "score": 100}]

        # Update with higher score
        result = player_data.update_player_score("ExistingPlayer", 200)

        # Should update local cache
        assert len(player_data.players) == 1
        assert player_data.players[0]["score"] == 200

        # Update with lower score (should keep higher score)
        result = player_data.update_player_score("ExistingPlayer", 50)
        assert player_data.players[0]["score"] == 200

        # Both updates should return success
        assert result is True

    def test_start_game_timer(self, mock_db):
        """
        Test starting game timer
        """
        player_data = PlayerData()

        # Mock time.time() to return a fixed value
        with patch('time.time', return_value=1000.0):
            player_data.start_game_timer()
            assert player_data.game_start_time == 1000.0

    def test_save_game_result_connected(self, mock_db):
        """
        Test saving game result when connected
        """
        player_data = PlayerData()

        # Set up game timer
        with patch('time.time', side_effect=[1000.0, 1060.5]):
            player_data.start_game_timer()  # Sets to 1000.0
            result = player_data.save_game_result("TestPlayer", 150, 10)  # time.time() returns 1060.5

        # Should call database method with correct duration
        mock_db.add_game_result.assert_called_once_with("TestPlayer", 10, 150, 60.5)

        # Timer should be reset
        assert player_data.game_start_time == 0

        # Should return success
        assert result is True

    def test_save_game_result_disconnected(self, mock_db):
        """
        Test saving game result when disconnected
        """
        mock_db.connect.return_value = False
        player_data = PlayerData()

        with patch('time.time', side_effect=[1000.0, 1060.5]):
            player_data.start_game_timer()
            result = player_data.save_game_result("TestPlayer", 150, 10)

        # Should not call database method
        mock_db.add_game_result.assert_not_called()

        # Should return failure
        assert result is False

    def test_save_game_result_without_timer(self, mock_db):
        """
        Test saving game result without starting timer
        """
        player_data = PlayerData()

        # Don't start timer (should use 0 duration)
        with patch('time.time', return_value=1060.5):
            result = player_data.save_game_result("TestPlayer", 150, 10)

        # Should call database method with 0 duration
        mock_db.add_game_result.assert_called_once_with("TestPlayer", 10, 150, 0)

        # Should return success
        assert result is True

    def test_get_player_history_connected(self, mock_db):
        """
        Test getting player history when connected
        """
        player_data = PlayerData()
        result = player_data.get_player_history("TestPlayer1")

        # Should call database method
        mock_db.get_player_results.assert_called_once_with("TestPlayer1", None)

        # Should return formatted game results
        assert len(result) == 2
        # Check structure
        for game in result:
            assert all(key in game for key in [
                "player_name", "map_size", "score", "duration", "date"
            ])
        # Check values
        assert result[0]["player_name"] == "TestPlayer1"
        assert result[1]["player_name"] == "TestPlayer1"
        assert result[0]["score"] == 100
        assert result[1]["score"] == 150

    def test_get_player_history_with_map_size(self, mock_db):
        """
        Test getting player history filtered by map size
        """
        player_data = PlayerData()
        result = player_data.get_player_history("TestPlayer1", map_size=10)

        # Should call database method with filter
        mock_db.get_player_results.assert_called_once_with("TestPlayer1", 10)

        # Results still returned as provided by mock
        assert len(result) == 2

    def test_get_player_history_disconnected(self, mock_db):
        """
        Test getting player history when disconnected
        """
        mock_db.connect.return_value = False
        player_data = PlayerData()
        result = player_data.get_player_history("TestPlayer1")

        # Should not call database method
        mock_db.get_player_results.assert_not_called()

        # Should return empty list
        assert result == []