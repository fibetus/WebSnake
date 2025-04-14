import pytest
from engine import move_snake, check_collision, is_within_bounds, increase_speed, Game

# move_snake tests:
def test_move_snake_up():
    """
    Check if the snake moves one unit upward when 'up' direction is given.
    The y-coordinate should decrease by 1.
    """
    assert move_snake((5, 5), "up") == (5, 4)

def test_move_snake_down():
    """
    Check if the snake moves one unit downward when 'down' direction is given.
    The y-coordinate should increase by 1.
    """
    assert move_snake((5, 5), "down") == (5, 6)

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
    Should return False when x is greater than the board width.
    """
    assert is_within_bounds((11, 5), (10, 10)) == False

def test_is_within_bounds_on_edge():
    """
    Check if a position on the board edge (0,0) is considered within bounds.
    Should return True since edge positions are valid game positions.
    """
    assert is_within_bounds((0, 0), (10, 10)) == True

def test_is_within_bounds_outside_board_with_negative_x():
    """
    Check if a position with negative x-coordinate is detected as out of bounds.
    Should return False since negative coordinates are outside the board.
    """
    assert is_within_bounds((-10, 0), (10, 10)) == False

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
    g.game_over = True
    g.update()
    assert g.snake == [(5, 5)]

def test_update_snake_move_after_init():
    """
    Check if the snake moves in the default direction (right) after initialization.
    After one update, the snake head should move from (5,5) to (6,5).
    """
    g = Game()
    assert g.snake == [(5, 5)]
    g.update()
    assert g.snake[0] == (6, 5)

def test_update_check_collision_with_wall():
    """
    Check if game_over flag is set when snake collides with the wall.
    When snake moves beyond board boundaries, the game should end.
    """
    g = Game(board_size=(10,10), initial_position=(9,5), direction="right")
    g.update()
    assert g.game_over is True

def test_update_eat_food():
    """
    Check if eating food increases score and snake length.
    When snake head position matches food position, score should increase and snake should grow.
    """
    g = Game(initial_position=(6,5))
    g.food = (7, 5)
    g.update()
    assert g.score == 1
    assert len(g.snake) == 2


# spawn_food tests:
def test_spawn_food_not_on_snake():
    """
    Check if food spawns in a location not occupied by the snake.
    Food should never be placed on the snake's body.
    """
    g = Game()
    g.snake = [(x, 0) for x in range(10)]
    g.spawn_food()
    assert g.food not in g.snake


# full game scenario tests:
def test_snake_eat_food_after_few_moves():
    """
    Check a complete gameplay scenario involving movement, direction change, and eating food.
    This integration test verifies multiple game mechanics working together correctly.
    """
    g = Game(board_size=(10, 10), initial_position=(5, 5), direction="right")
    g.food = (6, 3)
    g.update()
    g.change_direction("up")
    g.update()
    g.update()
    assert g.snake[0] == (6, 3)
    assert g.score == 1
    assert len(g.snake) == 2