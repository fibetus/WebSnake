import argparse
from engine import move_snake, check_collision, is_within_bounds, increase_speed, Game
from ui import UI
from data import PlayerData


def main():
    parser = argparse.ArgumentParser(description="Simple Snake Game in Python")
    parser.add_argument("--history", help="Displays the history of Snake Game", action="store_true")

    args = parser.parse_args()
    if args.history:
        print("History of the Snake Game:\n"
              "The Snake genre began with the 1976 arcade video game Blockade developed and published by Gremlin Industries.\n"
              "The first home computer version 'Worm' was programmed by Peter Trefonas for the TRS-80 and published in 1978.\n"
              "Fun Fact: The Snake on IBM PC was rendered in a text mode!")

    # Create player data storage
    player_data = PlayerData()

    # Create UI without a game instance yet (we'll create it after setup)
    ui = UI()

    # Show setup scene first
    ui.show_setup_scene(player_data)

    # Start the main game (the game instance is created during setup)
    ui.start()


if __name__ == '__main__':
    main()