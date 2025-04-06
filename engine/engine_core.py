class Game:
    def __init__(self, board_size=(10, 10), initial_position=(5, 5), direction="right"):
        self.board_size = board_size
        self.snake = [initial_position]
        self.direction = direction
        self.food = (7, 5)
        self.score = 0
        self.game_over = False
        self.speed = 1

    def update(self):
        if self.game_over:
            return

        new_head = move_snake(self.snake[0], self.direction)

        if not is_within_bounds(new_head, self.board_size) or new_head == self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if check_collision(new_head, self.food):
            self.score += 1
            self.speed = increase_speed(self.score)
            self.spawn_food()
        else:
            self.snake.pop()

    def spawn_food(self):
        from random import randint
        width, height = self.board_size
        while True:
            new_food = (randint(0, width - 1), randint(0, height - 1))
            if new_food not in self.snake:
                self.food = new_food
                break


    # checking if we don't change direction into snake body
    def change_direction(self, new_direction):
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
        if new_direction != opposites.get(self.direction):
            self.direction = new_direction



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