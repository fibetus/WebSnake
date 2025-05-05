import threading
import time
from .engine.engine_core import Game
from .database import db as database
import traceback

# --- Game State Management ---
game_instance = None
game_timer = None
game_lock = threading.Lock() # Lock for thread-safe access to shared resources
player_name_global = None
map_size_global = None
game_start_time = None
is_result_saved = False

def start_new_game(username, map_size):
    """
    Initializes a new game, creates player record, creates Game instance,
    and starts the game loop timer.
    """
    global game_instance, game_timer, player_name_global, map_size_global, game_start_time, is_result_saved
    print(f"Attempting to start new game for {username} size {map_size}")
    with game_lock:
        if game_timer:
            print("DEBUG: Cancelling existing game timer.")
            game_timer.cancel()
            game_timer = None

        player_name_global = username
        map_size_global = map_size
        game_start_time = time.time()
        is_result_saved = False

        print("Connecting DB...")
        if not database.connect():
            print("ERROR: Could not connect to database.")
            return False

        print(f"Ensuring player record for {username}...")
        try:
            player_id = database.add_player(name=username, map_size=map_size, score=0)
            if not player_id:
                print(f"WARN: Failed to ensure player record for {username}.")
        except Exception as e:
            print(f"ERROR during database.add_player: {e}")
            return False

        print("Creating Game instance...")
        try:
            game_instance = Game(board_size=(map_size, map_size))
            print(f"Game instance created. Speed: {game_instance.speed:.2f}")
        except Exception as e:
            print(f"ERROR creating Game instance: {e}")
            game_instance = None
            return False

        print(f"New game started log message for {username}...")


        print("Scheduling initial game update...")
        schedule_game_update()

        print("start_new_game completed successfully.")
        return True

def schedule_game_update():
    """
    Schedules the next call to update_game_state using threading.Timer.
    This function should only be called when holding the game_lock.
    """
    global game_timer, game_instance
    if game_timer:
        game_timer.cancel()
        game_timer = None

    if game_instance and not game_instance.game_over:
        interval = 1.0 / game_instance.speed if game_instance.speed > 0 else 1.0
        game_timer = threading.Timer(interval, update_game_state_wrapper)
        game_timer.daemon = True
        game_timer.start()
    else:
        print("DEBUG: Not scheduling update (game over or no instance).")


def update_game_state_wrapper():
    """
    Wrapper function to acquire the lock before calling the main update logic.
    This is the function the Timer will actually call.
    """
    with game_lock:
        update_game_state()

def update_game_state():
    """
    Updates the game state by calling the engine's update method.
    Handles game over logic and result saving.
    Schedules the next update if the game is still running.
    Assumes game_lock is already held by the caller (update_game_state_wrapper).
    """
    global game_instance, is_result_saved, game_start_time, player_name_global, map_size_global

    if not game_instance:
        print("Warning: update_game_state called without active game instance.")
        return

    if not game_instance.game_over:
        try:
            game_instance.update()
        except Exception as e:
             print(f"ERROR during game_instance.update(): {e}")
             game_instance.game_over = True

        if game_instance.game_over and not is_result_saved:
            print(f"Game over detected for {player_name_global}. Final score: {game_instance.score}")
            if database.is_connected and player_name_global and game_start_time:
                duration = time.time() - game_start_time
                try:
                    result_id = database.add_game_result(
                        player_name=player_name_global,
                        map_size=map_size_global,
                        score=game_instance.score,
                        duration=duration
                    )
                    if result_id:
                        print(f"Game result saved successfully (ID: {result_id}).")
                        is_result_saved = True
                    else:
                         print("Error: Failed to save game result to database (add_game_result returned None/False).")
                except Exception as e:
                     print(f"ERROR during database.add_game_result: {e}")
            else:
                print("Warning: Cannot save result - DB not connected or player info missing.")

        elif not game_instance.game_over:
             # If game is still running, schedule the next update
             schedule_game_update()


def get_current_state():
    """
    Retrieves the current state of the game instance.
    """
    global game_instance
    with game_lock:
        if game_instance:
            try:
                state = {
                    "snake": game_instance.snake,
                    "food": game_instance.food,
                    "score": game_instance.score,
                    "game_over": game_instance.game_over,
                    "board_size": list(game_instance.board_size),
                    "speed": game_instance.speed
                }
                return state
            except Exception as e:
                 print(f"ERROR in get_current_state: {e}")
        return {
            "snake": [], "food": None, "score": 0, "game_over": True,
            "board_size": [10, 10], "speed": 0
        }


def process_move(direction):
    """
    Processes a player's move request by changing the snake's direction.
    Acquires lock only for the direction change, then releases it before getting state.
    """
    global game_instance, player_name_global
    print(f"DEBUG [game_manager]: Entered process_move with direction '{direction}'") # Log entry

    processed_successfully = False
    with game_lock: # Acquire lock ONLY for accessing/modifying game_instance directly
        if game_instance and not game_instance.game_over:
            try:
                game_instance.change_direction(direction)
                print(f"DEBUG [game_manager]: game_instance.change_direction('{direction}') called.")
                processed_successfully = True
            except Exception as e:
                 print(f"ERROR [game_manager]: Exception during game_instance.change_direction: {e}")
                 traceback.print_exc() # Print traceback on error
        elif game_instance and game_instance.game_over:
             print("DEBUG [game_manager]: Move ignored: Game is already over.")
        else:
             print("DEBUG [game_manager]: Move ignored: No active game instance.")


    if processed_successfully:
        print(f"DEBUG [game_manager]: process_move finished processing '{direction}'. Now getting current state...")
    else:
        print(f"DEBUG [game_manager]: process_move did not change direction. Getting current state...")

    return get_current_state()

