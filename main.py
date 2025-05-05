import argparse
from game_api.pygame_ui import UI
from game_api.data import PlayerData


def main():
    parser = argparse.ArgumentParser(description="Simple Snake Game in Python")
    parser.add_argument("--history", help="Displays the history of Snake Game", action="store_true")
    parser.add_argument("--scores", help="Displays high scores from the database", action="store_true")
    parser.add_argument("--map-size", type=int, help="Filter high scores by map size (optional)")

    args = parser.parse_args()
    if args.history:
        print("History of the Snake Game:\n"
              "The Snake genre began with the 1976 arcade video game Blockade developed and published by Gremlin Industries.\n"
              "The first home computer version 'Worm' was programmed by Peter Trefonas for the TRS-80 and published in 1978.\n"
              "Fun Fact: The Snake on IBM PC was rendered in a text mode!")

    # Create player data storage
    player_data = PlayerData()

    # Handling --scores argument for leaderboard
    if args.scores:
        # Display high scores from database
        map_filter = args.map_size
        high_scores = player_data.get_high_scores(limit=10, map_size=map_filter)

        print("\n===== HIGH SCORES =====")
        if map_filter:
            print(f"Filtered by map size: {map_filter}x{map_filter}")
        else:
            print("All map sizes")

        if not high_scores:
            print("No scores found!")
        else:
            for i, player in enumerate(high_scores, 1):
                map_size = player.get('map_size', 'N/A')
                print(f"{i}. {player['name']}: {player['score']} points (Map: {map_size}x{map_size if map_size != 'N/A' else 'N/A'})")

        print("=======================\n")
        return

    # Create UI without a game instance yet (we'll create it after setup)
    ui = UI()

    # Show setup scene first
    ui.show_setup_scene(player_data)

    # Start the main game (the game instance is created during setup)
    ui.start()


if __name__ == '__main__':
    main()