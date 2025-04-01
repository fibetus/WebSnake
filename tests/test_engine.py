import pytest
from engine import move_snake, check_collision, is_within_bounds

# move_snake tests:
def test_move_snake_up():
    assert move_snake((5, 5), "up") == (4, 5)

def test_move_snake_down():
    assert move_snake((5, 5), "down") == (6, 5)

def test_move_snake_left():
    assert move_snake((5, 5), "left") == (5, 4)

def test_move_snake_right():
    assert move_snake((5, 5), "right") == (5, 6)

def test_move_snake_invalid_direction():
    with pytest.raises(ValueError):
        move_snake((5, 5), "diagonal")


# check_collision tests:
def test_check_collision_when_position_collides():
    assert check_collision((5, 5), (5, 5)) == True

def test_check_collision_when_position_doesnt_collide():
    assert check_collision((5, 5), (4,5)) == False


# is_within_bounds tests:
def test_is_within_bounds_inside_board():
    assert is_within_bounds((4, 5), (10, 10)) == True

def test_is_within_bounds_outside_board():
    assert is_within_bounds((11, 5), (10, 10)) == False

def test_is_within_bounds_on_edge():
    assert is_within_bounds((0, 0), (10, 10)) == True