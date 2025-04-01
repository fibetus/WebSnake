def move_snake(position, direction):
    x, y = position
    if direction == "up":
        return (x, y + 1)
    elif direction == "down":
        return (x, y - 1)
    elif direction == "left":
        return (x - 1, y)
    elif direction == "right":
        return (x + 1, y)
    else:
        raise ValueError(f"Invalid direction: {direction}")

def check_collision(position1, position2):
    return position1 == position2

def is_within_bounds(position, board_size):
    x, y = position
    width, height = board_size
    return 0 <= x < width and 0 <= y < height

def increase_speed(score):
    starting_speed = 1
    max_speed = 2
    current_speed = starting_speed + (score // 3) * 0.1
    return min(current_speed, max_speed)