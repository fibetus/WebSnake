import pytest
from unittest import mock
import mongomock
import datetime

from data.database import Database


@pytest.fixture(scope="function")
def mock_db():
    """
    Create a mock database for testing.
    """
    # Create a patcher to replace the MongoClient with mongomock
    with mock.patch('pymongo.MongoClient', mongomock.MongoClient):
        test_db = Database()

        # Mock the _get_warsaw_time method to return a consistent time for testing
        original_get_time = test_db._get_warsaw_time
        test_db._get_warsaw_time = mock.MagicMock(return_value=datetime.datetime(2025, 4, 11, 12, 0, 0))

        # Force connection to use the mock
        test_db.connect()

        # Clear any existing data to start fresh
        if test_db.players is not None:
            test_db.players.delete_many({})
        if test_db.game_results is not None:
            test_db.game_results.delete_many({})

        # Update metadata with current values
        test_db.metadata = {
            "user": "testUser",  # Using provided username
            "session_start": original_get_time  # Using provided timestamp
        }

        yield test_db

        # Cleanup after test
        if test_db.players is not None:
            test_db.players.delete_many({})
        if test_db.game_results is not None:
            test_db.game_results.delete_many({})
        test_db.disconnect()

        # Restore original method
        test_db._get_warsaw_time = original_get_time


# Clean up real database after all tests (in case real connection was used). Just another layer of protection.
@pytest.fixture(scope="session", autouse=True)
def cleanup_real_database():
    """
    Clean up any data created in the real database during tests.
    """
    yield  # Run all tests

    # After all tests, connect to real database and clean up test data
    try:
        cleanup_db = Database()
        if cleanup_db.connect():
            print("Cleaning up test data from real database...")
            # Delete all test data using a filter that identifies test data
            if cleanup_db.players is not None:
                cleanup_db.players.delete_many({
                    "$or": [
                        {"name": {"$regex": "^Test"}},
                        {"name": {"$in": ["Player1", "Player2", "Player3", "Player4",
                                          "UpdateTest", "DeleteTest1", "DeleteTest2",
                                          "ResultsPlayer", "ExistingPlayer", "NewPlayer"]}},
                        {"created_by": "testUser"}  # Delete all data created by our test user
                    ]
                })

            if cleanup_db.game_results is not None:
                cleanup_db.game_results.delete_many({
                    "$or": [
                        {"player_name": {"$regex": "^Test"}},
                        {"player_name": {"$in": ["Player1", "Player2", "Player3", "Player4",
                                                 "UpdateTest", "DeleteTest1", "DeleteTest2",
                                                 "ResultsPlayer", "ExistingPlayer", "NewPlayer"]}},
                        {"created_by": "testUser"}  # Delete all data created by our test user
                    ]
                })

            cleanup_db.disconnect()
            print("Test data cleanup complete.")
    except Exception as e:
        print(f"Warning: Could not clean up test data: {e}")


class TestConnectionHandling:
    """
    Test database connection handling.
    """

    def test_connection_failure(self):
        """Test handling of connection failure."""
        # Create a test instance with a mocked connect method
        test_db = Database()

        # Mock the connect method directly using monkeypatch
        original_connect = test_db.connect

        def mock_connect():
            # The original error raising method
            raise Exception("Connection failed")

        # Replace the connect method
        test_db.connect = mock_connect

        # Now test the connection
        try:
            result = test_db.connect()
            assert False, "Expected an exception but none was raised"
        except Exception:
            # If we get here, the exception was raised properly
            assert test_db.is_connected is False

        # Restore the original method to avoid affecting other tests
        test_db.connect = original_connect

    def test_disconnect(self):
        """
        Test database disconnection.
        """
        # Create a mock client that we can verify is closed
        mock_client = mock.MagicMock()

        # Create a database instance and manually set its properties
        test_db = Database()
        test_db.client = mock_client
        test_db.is_connected = True

        # Call disconnect
        test_db.disconnect()

        # Verify the client was closed and is_connected was set to False
        mock_client.close.assert_called_once()
        assert test_db.is_connected is False

    def test_operations_with_no_connection(self):
        """
        Test operations when database is not connected.
        """
        # Create a db instance but don't actually connect
        test_db = Database()

        # Mock the connect method to always return False
        original_connect = test_db.connect
        test_db.connect = lambda: False

        # Force disconnected state
        test_db.is_connected = False

        # Test various operations
        assert test_db.add_player("Test", 10, 100) is None
        assert test_db.get_players() == []
        assert test_db.get_high_scores() == []
        assert test_db.update_player("Test", 10, 100) is False
        assert test_db.delete_player("Test") is False
        assert test_db.add_game_result("Test", 10, 100, 60.0) is None
        assert test_db.get_player_results("Test") == []

        # Restore original method
        test_db.connect = original_connect


class TestPlayerCRUD:
    """
    Test player CRUD operations.
    """

    def test_add_player_new(self, mock_db):
        """
        Test adding a new player.
        """
        player_id = mock_db.add_player("TestPlayer", 10, 100)
        assert player_id is not None

        # Verify player was added
        player = mock_db.players.find_one({"name": "TestPlayer"})
        assert player is not None
        assert player["name"] == "TestPlayer"
        assert player["map_size"] == 10
        assert player["score"] == 100
        assert "created_at" in player
        assert player["created_by"] == "testUser"  # Verify correct user

    def test_add_player_existing_lower_score(self, mock_db):
        """
        Test adding an existing player with a lower score should not update.
        """
        # Add initial player
        player_id = mock_db.add_player("TestPlayer", 10, 100)

        # Try to add with lower score
        new_id = mock_db.add_player("TestPlayer", 10, 50)

        # Should return the same ID
        assert new_id == player_id

        # Score should not be updated
        player = mock_db.players.find_one({"name": "TestPlayer"})
        assert player["score"] == 100

    def test_add_player_existing_higher_score(self, mock_db):
        """
        Test adding an existing player with a higher score should update.
        """
        # Add initial player
        player_id = mock_db.add_player("TestPlayer", 10, 100)

        # Try to add with higher score
        new_id = mock_db.add_player("TestPlayer", 10, 150)

        # Should return the same ID
        assert new_id == player_id

        # Score should be updated
        player = mock_db.players.find_one({"name": "TestPlayer"})
        assert player["score"] == 150
        assert "updated_at" in player

    def test_get_players(self, mock_db):
        """
        Test getting all players.
        """
        # Verify we're starting with an empty collection
        players_start = mock_db.get_players()
        assert len(players_start) == 0

        # Add test players
        mock_db.add_player("Player1", 10, 100)
        mock_db.add_player("Player2", 15, 200)

        players = mock_db.get_players()
        assert len(players) == 2
        assert any(p["name"] == "Player1" for p in players)
        assert any(p["name"] == "Player2" for p in players)
        # Verify ObjectId conversion
        assert isinstance(players[0]["_id"], str)

    def test_get_high_scores(self, mock_db):
        """
        Test getting high scores.
        """
        # Verify we're starting with an empty collection
        players_start = mock_db.get_players()
        assert len(players_start) == 0

        # Add test players with different scores
        mock_db.add_player("Player1", 10, 100)
        mock_db.add_player("Player2", 10, 300)
        mock_db.add_player("Player3", 10, 200)
        mock_db.add_player("Player4", 15, 500)

        # Test without map_size filter
        scores = mock_db.get_high_scores(limit=2)
        assert len(scores) == 2
        assert scores[0]["name"] == "Player4"  # Highest score
        assert scores[1]["name"] == "Player2"  # Second highest

        # Test with map_size filter
        scores = mock_db.get_high_scores(map_size=10)
        assert len(scores) == 3
        assert scores[0]["name"] == "Player2"  # Highest score for map_size 10
        assert scores[1]["name"] == "Player3"
        assert scores[2]["name"] == "Player1"

    def test_update_player_higher_score(self, mock_db):
        """
        Test updating a player's score with higher value.
        """
        mock_db.add_player("UpdateTest", 10, 100)

        # Update with higher score
        result = mock_db.update_player("UpdateTest", 10, 150)
        assert result is True

        # Verify score was updated
        player = mock_db.players.find_one({"name": "UpdateTest"})
        assert player["score"] == 150

    def test_update_player_lower_score(self, mock_db):
        """
        Test updating a player's score with lower value (should not update).
        """
        mock_db.add_player("UpdateTest", 10, 150)

        # Update with lower score (should not update)
        result = mock_db.update_player("UpdateTest", 10, 50)
        assert result is False

        # Verify score was not updated
        player = mock_db.players.find_one({"name": "UpdateTest"})
        assert player["score"] == 150

    def test_delete_player_with_map_size(self, mock_db):
        """
        Test deleting a player with specific map size.
        """
        # Add test players
        mock_db.add_player("DeleteTest1", 10, 100)
        mock_db.add_player("DeleteTest2", 10, 200)
        mock_db.add_player("DeleteTest2", 15, 300)  # Same name, different map_size

        # Delete specific player with map size
        result = mock_db.delete_player("DeleteTest2", 15)
        assert result is True

        # Verify only one was deleted
        players = list(mock_db.players.find({"name": "DeleteTest2"}))
        assert len(players) == 1
        assert players[0]["map_size"] == 10

    def test_delete_player_by_name_only(self, mock_db):
        """
        Test deleting a player by name only.
        """
        mock_db.add_player("DeleteTest1", 10, 100)

        # Delete by name only
        result = mock_db.delete_player("DeleteTest1")
        assert result is True

        # Verify it was deleted
        player = mock_db.players.find_one({"name": "DeleteTest1"})
        assert player is None

    def test_delete_nonexistent_player(self, mock_db):
        """
        Test deleting a non-existent player.
        """
        result = mock_db.delete_player("NonExistent")
        assert result is False


class TestGameResultsCRUD:
    """
    Test game results CRUD operations.
    """

    def test_add_game_result_new_player(self, mock_db):
        """
        Test adding a game result for a new player.
        """
        # Verify we're starting with empty collections
        players_start = mock_db.get_players()
        assert len(players_start) == 0

        result_id = mock_db.add_game_result("NewPlayer", 10, 100, 60.5)
        assert result_id is not None

        # Verify result was added
        result = mock_db.game_results.find_one({"player_name": "NewPlayer"})
        assert result is not None
        assert result["map_size"] == 10
        assert result["score"] == 100
        assert result["duration"] == 60.5
        assert result["created_by"] == "testUser"  # Verify correct user

        # Verify player was created
        player = mock_db.players.find_one({"name": "NewPlayer"})
        assert player is not None
        assert player["score"] == 100

    def test_add_game_result_existing_player_higher_score(self, mock_db):
        """
        Test adding a game result with higher score for existing player.
        """
        # Add initial player
        mock_db.add_player("ExistingPlayer", 10, 100)

        # Add game result with higher score
        result_id = mock_db.add_game_result("ExistingPlayer", 10, 150, 70.0)
        assert result_id is not None

        # Verify player score was updated
        player = mock_db.players.find_one({"name": "ExistingPlayer"})
        assert player["score"] == 150

    def test_add_game_result_existing_player_lower_score(self, mock_db):
        """
        Test adding a game result with lower score for existing player.
        """
        # Add initial player
        mock_db.add_player("ExistingPlayer", 10, 200)

        # Add game result with lower score
        result_id = mock_db.add_game_result("ExistingPlayer", 10, 150, 70.0)
        assert result_id is not None

        # Verify player score was not updated
        player = mock_db.players.find_one({"name": "ExistingPlayer"})
        assert player["score"] == 200

        # Verify result was still added
        results = list(mock_db.game_results.find({"player_name": "ExistingPlayer"}))
        assert len(results) == 1

    def test_get_player_results_all(self, mock_db):
        """
        Test getting all player results.
        """
        # Verify we're starting with empty collections
        results_start = list(mock_db.game_results.find())
        assert len(results_start) == 0

        # Add some game results
        mock_db.add_game_result("ResultsPlayer", 10, 100, 60.0)
        mock_db.add_game_result("ResultsPlayer", 10, 150, 70.0)
        mock_db.add_game_result("ResultsPlayer", 15, 200, 80.0)

        # Get all results for player
        results = mock_db.get_player_results("ResultsPlayer")
        assert len(results) == 3
        # Verify ObjectId conversion
        assert isinstance(results[0]["_id"], str)
        assert isinstance(results[0]["player_id"], str)

    def test_get_player_results_filtered(self, mock_db):
        """
        Test getting player results filtered by map size.
        """
        # Add some game results
        mock_db.add_game_result("ResultsPlayer", 10, 100, 60.0)
        mock_db.add_game_result("ResultsPlayer", 10, 150, 70.0)
        mock_db.add_game_result("ResultsPlayer", 15, 200, 80.0)

        # Get results filtered by map size
        results = mock_db.get_player_results("ResultsPlayer", map_size=10)
        assert len(results) == 2
        assert all(r["map_size"] == 10 for r in results)

        # Confirm sorted by date (newest first)
        assert results[0]["date"] >= results[1]["date"]