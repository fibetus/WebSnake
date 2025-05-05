class Game:
    def __init__(self, board_size=(10, 10), initial_position=None, direction="right"):
        """
        Initialize the game with a board size and initial position.
        Args:
            board_size (tuple): the size of the game board.
            initial_position (tuple): the initial position of the snake.
            direction: the initial direction of the snake.
        """
        self.board_size = board_size
        width, height = board_size

        if initial_position is None:
            initial_position = (width // 2, height // 2)

        init_x = max(0, min(initial_position[0], width - 1))
        init_y = max(0, min(initial_position[1], height - 1))
        self.snake = [(init_x, init_y)]

        self.direction = direction
        self.score = 0
        self.game_over = False
        self.speed = 1

        self.food = None
        self.spawn_food()

    def update(self):
        """
        Update the snake, used in the game loop.
        """
        if self.game_over:
            return

        new_head = move_snake(self.snake[0], self.direction)

        # Checking if snake isn't within bounds
        if not is_within_bounds(new_head, self.board_size):
            self.game_over = True
            return

        # Checking if snake isn't inside itself
        for segment in self.snake[:-1]:
            if check_collision(new_head, segment):
                self.game_over = True
                return

        # Add "tail" to snake (more like adding new head and old head becomes tail)
        self.snake.insert(0, new_head)

        # Check if we've eaten food
        if self.food and check_collision(new_head, self.food):
            self.score += 1
            self.speed = increase_speed(self.score)
            self.spawn_food()
        else:
            self.snake.pop()  # Pop if we don't eat anything

    def spawn_food(self):
        """
        Provides spawning of the food in the random location.
        """
        width, height = self.board_size

        # Create a set of all possible positions
        all_positions = set((x, y) for x in range(width) for y in range(height))
        snake_positions = set(self.snake)
        available_positions = list(all_positions - snake_positions)

        # If there are available positions, choose one randomly
        if available_positions:
            import random
            self.food = random.choice(available_positions)
        else:
            # No available positions, game won
            self.food = None
            self.game_over = True

    # Checking if we don't change direction into snake body
    def change_direction(self, new_direction):
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
        if len(self.snake) <= 1 or new_direction != opposites.get(self.direction):
            self.direction = new_direction


def move_snake(position, direction):
    """
    Provides the snake movement logic.
    Args:
        position (tuple): the position of the snake.
        direction (str): the initial direction of the snake.
    """
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
    """
    Checks if two positions collide.
    Args:
        position1 (tuple): the position of the one object.
        position2 (tuple): the position of the other object.
    """
    return position1 == position2


def is_within_bounds(position, board_size):
    """
    Checks if the snake is within the bounds of the board.
    Args:
         position (tuple): the position of the snake.
         board_size (tuple): the size of the board.
    """
    x, y = position
    width, height = board_size
    return 0 <= x < width and 0 <= y < height

def increase_speed(score):
    """
    Provides the speed increased by the food the snake ate.
    """
    starting_speed = 1
    max_speed = 2
    current_speed = starting_speed + (score // 3) * 0.1
    return min(current_speed, max_speed)