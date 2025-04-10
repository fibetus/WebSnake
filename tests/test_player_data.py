import pytest
from data import PlayerData

# testing the initialization of PlayerData
def test_player_data_init():
    pd = PlayerData()
    assert pd.players == []

# testing add_player method
def test_add_player_with_default_score():
    pd = PlayerData()
    pd.add_player("TestPlayer")
    assert len(pd.players) == 1
    assert pd.players[0]["name"] == "TestPlayer"
    assert pd.players[0]["score"] == 0

def test_add_player_with_custom_score():
    pd = PlayerData()
    pd.add_player("TestPlayer", 100)
    assert len(pd.players) == 1
    assert pd.players[0]["name"] == "TestPlayer"
    assert pd.players[0]["score"] == 100

def test_add_multiple_players():
    pd = PlayerData()
    pd.add_player("Player1")
    pd.add_player("Player2", 50)
    pd.add_player("Player3", 75)
    assert len(pd.players)
