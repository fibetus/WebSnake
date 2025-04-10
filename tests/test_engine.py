import pytest
from engine import move_snake, check_collision, is_within_bounds, increase_speed, Game

# move_snake tests:
def test_move_snake_up():
    assert move_snake((5, 5), "up") == (5, 6)

def test_move_snake_down():
    assert move_snake((5, 5), "down") == (5, 4)

def test_move_snake_left():
    assert move_snake((5, 5), "left") == (4, 5)

def test_move_snake_right():
    assert move_snake((5, 5), "right") == (6, 5)

def test_move_snake_invalid_direction():
    with pytest.raises(ValueError):
        move_snake((5, 5), "straight")


# check_collision tests:
def test_check_collision_when_position_collides():
    assert check_collision((5, 5), (5, 5)) == True

def test_check_collision_when_position_doesnt_collide():
    assert check_collision((5, 5), (4,5)) == False


# is_within_bounds tests:
def test_is_within_bounds_inside_board():
    assert is_within_bounds((4, 5), (10, 10)) == True

def test_is_within_bounds_outside_board_with_positive_x_and_y():
    assert is_within_bounds((11, 5), (10, 10)) == False

def test_is_within_bounds_on_edge():
    assert is_within_bounds((0, 0), (10, 10)) == True

def test_is_within_bounds_outside_board_with_negative_x():
    assert is_within_bounds((-10, 0), (10, 10)) == False

def test_is_within_bounds_outside_board_with_negative_y():
    assert is_within_bounds((3, -1), (10, 10)) == False


# increase_speed tests:
def test_increase_speed_beginning():
    assert increase_speed(0) == 1

def test_increase_speed_after_3_apples():
    assert increase_speed(3) == 1.1

def test_increase_speed_max_speed():
    assert increase_speed(30) == 2


# change_direction tests:
def test_change_direction_valid():
    g = Game()
    g.direction = "up"
    g.change_direction("left")
    assert g.direction == "left"

def test_change_direction_invalid():
    g = Game()
    g.direction = "down"
    g.change_direction("up")
    assert g.direction == "down"


# update tests:
def test_update_game_over():
    g = Game()
    g.game_over = True
    g.update()
    assert g.snake == [(5, 5)]

def test_update_snake_move_after_init():
    g = Game()
    assert g.snake == [(5, 5)]
    g.update()
    assert g.snake[0] == (6, 5)

def test_update_check_collision_with_wall():
    g = Game(board_size=(10,10), initial_position=(9,5), direction="right")
    g.update()
    assert g.game_over is True

def test_update_eat_food():
    g = Game(initial_position=(6,5))
    g.food = (7, 5)
    g.update()
    assert g.score == 1
    assert len(g.snake) == 2


# spawn_food tests:
def test_spawn_food_not_on_snake():
    g = Game()
    g.snake = [(x, 0) for x in range(10)]
    g.spawn_food()
    assert g.food not in g.snake


# full game scenario tests:
def test_snake_eat_food_after_few_moves():
    g = Game(board_size=(10, 10), initial_position=(5, 5), direction="right")
    g.food = (6, 7)
    g.update()
    g.change_direction("up")
    g.update()
    g.update()
    assert g.snake[0] == (6, 7)
    assert g.score == 1
    assert len(g.snake) == 2

