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
    return x >= 0 and x < width and y >= 0 and y < height

def increase_speed(score):
    startingSpeed = 1
    maxSpeed = 2
    speed = startingSpeed + (score // 3) * 0.1
    return min(speed, maxSpeed)