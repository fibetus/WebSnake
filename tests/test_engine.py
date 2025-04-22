import pytest
from engine import move_snake, check_collision, is_within_bounds, increase_speed, Game

# move_snake tests:
def test_move_snake_up():
    """
    Check if the snake moves one unit upward when 'up' direction is given (Cartesian).
    The y-coordinate should increase by 1.
    """
    assert move_snake((5, 5), "up") == (5, 6) # Changed expectation for Cartesian

def test_move_snake_down():
    """
    Check if the snake moves one unit downward when 'down' direction is given (Cartesian).
    The y-coordinate should decrease by 1.
    """
    assert move_snake((5, 5), "down") == (5, 4) # Changed expectation for Cartesian

def test_move_snake_left():
    """
    Check if the snake moves one unit to the left when 'left' direction is given.
    The x-coordinate should decrease by 1.
    """
    assert move_snake((5, 5), "left") == (4, 5)

def test_move_snake_right():
    """
    Check if the snake moves one unit to the right when 'right' direction is given.
    The x-coordinate should increase by 1.
    """
    assert move_snake((5, 5), "right") == (6, 5)

def test_move_snake_invalid_direction():
    """
    Check if the function raises a ValueError when an invalid direction is provided.
    Only 'up', 'down', 'left', and 'right' should be valid directions.
    """
    with pytest.raises(ValueError):
        move_snake((5, 5), "straight")


# check_collision tests:
def test_check_collision_when_position_collides():
    """
    Check if collision is detected when two positions are exactly the same.
    Should return True when positions are identical.
    """
    assert check_collision((5, 5), (5, 5)) == True

def test_check_collision_when_position_doesnt_collide():
    """
    Check if collision is correctly not detected when positions are different.
    Should return False when positions are not identical.
    """
    assert check_collision((5, 5), (4,5)) == False


# is_within_bounds tests:
def test_is_within_bounds_inside_board():
    """
    Check if a position inside the board boundaries is correctly identified.
    Should return True for a position that is within the board dimensions.
    """
    assert is_within_bounds((4, 5), (10, 10)) == True

def test_is_within_bounds_outside_board_with_positive_x_and_y():
    """
    Check if a position with x-coordinate exceeding board width is detected as out of bounds.
    Should return False when x is greater than or equal to the board width.
    """
    assert is_within_bounds((10, 5), (10, 10)) == False # x must be < width
    assert is_within_bounds((5, 10), (10, 10)) == False # y must be < height

def test_is_within_bounds_on_edge():
    """
    Check if a position on the board edge (0,0) is considered within bounds.
    Should return True since edge positions are valid game positions.
    """
    assert is_within_bounds((0, 0), (10, 10)) == True
    assert is_within_bounds((9, 9), (10, 10)) == True # Check top-right corner

def test_is_within_bounds_outside_board_with_negative_x():
    """
    Check if a position with negative x-coordinate is detected as out of bounds.
    Should return False since negative coordinates are outside the board.
    """
    assert is_within_bounds((-1, 0), (10, 10)) == False

def test_is_within_bounds_outside_board_with_negative_y():
    """
    Check if a position with negative y-coordinate is detected as out of bounds.
    Should return False since negative coordinates are outside the board.
    """
    assert is_within_bounds((3, -1), (10, 10)) == False


# increase_speed tests:
def test_increase_speed_beginning():
    """
    Check if speed factor is 1 at the beginning of the game (score = 0).
    The initial speed multiplier should be 1.
    """
    assert increase_speed(0) == 1

def test_increase_speed_after_3_apples():
    """
    Check if speed increases to 1.1 after eating 3 apples (score = 3).
    Speed should increase incrementally as score increases.
    """
    assert increase_speed(3) == 1.1

def test_increase_speed_max_speed():
    """
    Check if speed is capped at 2 when score is very high (score = 30).
    There should be a maximum speed limit to keep the game playable.
    """
    assert increase_speed(30) == 2


# change_direction tests:
def test_change_direction_valid():
    """
    Check if the snake's direction changes to a valid new direction.
    Should allow changing from up to left (perpendicular directions).
    """
    g = Game()
    g.direction = "up"
    g.change_direction("left")
    assert g.direction == "left"

def test_change_direction_invalid():
    """
    Check if the snake's direction doesn't change when trying to reverse direction.
    Should prevent changing from down to up (opposite directions) for gameplay reasons.
    """
    g = Game()
    g.direction = "down"
    g.change_direction("up")
    assert g.direction == "down"


# update tests:
def test_update_game_over():
    """
    Check if the game state doesn't change when game is already over.
    When game_over is True, the snake should not move during update.
    """
    g = Game()
    initial_snake_pos = g.snake[:] # Copy initial position
    g.game_over = True
    g.update()
    assert g.snake == initial_snake_pos # Check it hasn't changed

def test_update_snake_move_after_init():
    """
    Check if the snake moves in the default direction (right) after initialization.
    After one update, the snake head should move from (5,5) to (6,5).
    """
    g = Game(board_size=(10,10)) # Initial pos (5,5)
    assert g.snake == [(5, 5)]
    g.update() # Default direction is 'right'
    assert g.snake == [(6, 5)] # Head moved right

def test_update_check_collision_with_wall():
    """
    Check if game_over flag is set when snake collides with the wall (Cartesian).
    When snake moves beyond board boundaries, the game should end.
    """
    # Test collision with right wall
    g_right = Game(board_size=(10,10), initial_position=(9,5), direction="right")
    g_right.update()
    assert g_right.game_over is True

    # Test collision with top wall (y=10)
    g_up = Game(board_size=(10,10), initial_position=(5,9), direction="up")
    g_up.update()
    assert g_up.game_over is True

    # Test collision with left wall (x=-1)
    g_left = Game(board_size=(10,10), initial_position=(0,5), direction="left")
    g_left.update()
    assert g_left.game_over is True

    # Test collision with bottom wall (y=-1)
    g_down = Game(board_size=(10,10), initial_position=(5,0), direction="down")
    g_down.update()
    assert g_down.game_over is True


def test_update_eat_food():
    """
    Check if eating food increases score and snake length.
    When snake head position matches food position, score should increase and snake should grow.
    """
    g = Game(initial_position=(6,5), direction="right", board_size=(10,10))
    g.food = (7, 5) # Place food directly in front
    g.update() # Snake moves to (7, 5) and eats food
    assert g.score == 1
    assert len(g.snake) == 2
    assert g.snake == [(7, 5), (6, 5)] # New head at (7,5), old head at (6,5)


# spawn_food tests:
def test_spawn_food_not_on_snake():
    """
    Check if food spawns in a location not occupied by the snake.
    Food should never be placed on the snake's body.
    """
    g = Game(board_size=(10,10))
    # Make snake fill most of the board except one spot
    g.snake = [(x, y) for x in range(10) for y in range(10)]
    g.snake.remove((5,5)) # Leave one spot open
    g.spawn_food()
    assert g.food == (5, 5) # Food must spawn in the only available spot
    assert g.food not in g.snake


# full game scenario tests:
def test_snake_eat_food_after_few_moves_cartesian():
    """
    Check a gameplay scenario involving movement, direction change, and eating food (Cartesian).
    This integration test verifies multiple game mechanics working together correctly.
    """
    g = Game(board_size=(10, 10), initial_position=(5, 5), direction="right")
    # Place food where the snake will be after moving right, then up twice
    g.food = (6, 7)
    # Move 1: right
    g.update() # Snake head at (6, 5), body at [(6, 5)]
    assert g.snake == [(6, 5)]
    # Move 2: change direction up, move
    g.change_direction("up")
    g.update() # Snake head at (6, 6), body at [(6, 6), (6, 5)]
    assert g.snake == [(6, 6)]
    # Move 3: move up again (eats food)
    g.update() # Snake head at (6, 7), body at [(6, 7), (6, 6), (6, 5)]
    assert g.snake[0] == (6, 7) # Head is at food location
    assert g.score == 1 # Score increased
    assert len(g.snake) == 2 # Snake length increased by 1