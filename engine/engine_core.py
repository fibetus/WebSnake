class Game:
    def __init__(self, board_size=(10, 10), initial_position=None, direction="right"):
        self.board_size = board_size
        width, height = board_size

        # Set default initial position at center if not provided
        if initial_position is None:
            initial_position = (width // 2, height // 2)

        # Make sure initial position is within bounds
        init_x = max(0, min(initial_position[0], width - 1))
        init_y = max(0, min(initial_position[1], height - 1))
        self.snake = [(init_x, init_y)]

        self.direction = direction
        self.score = 0
        self.game_over = False
        self.speed = 1

        # Initialize food to None
        self.food = None
        # Spawn food after initializing snake
        self.spawn_food()

    def update(self):
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
        width, height = self.board_size

        # Create a set of all possible positions
        all_positions = set((x, y) for x in range(width) for y in range(height))

        # Create a set of occupied positions (snake segments)
        snake_positions = set(self.snake)

        # Get available positions by removing snake positions from all positions
        available_positions = list(all_positions - snake_positions)

        # If there are available positions, choose one randomly
        if available_positions:
            import random
            self.food = random.choice(available_positions)
        else:
            # No available positions, game won
            self.game_over = True

    # Checking if we don't change direction into snake body
    def change_direction(self, new_direction):
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
        if new_direction != opposites.get(self.direction):
            self.direction = new_direction


# Snake movement
def move_snake(position, direction):
    x, y = position
    if direction == "up":
        return (x, y - 1)
    elif direction == "down":
        return (x, y + 1)
    elif direction == "left":
        return (x - 1, y)
    elif direction == "right":
        return (x + 1, y)
    else:
        raise ValueError(f"Invalid direction: {direction}")

# Shecking collision with any sort of objects
def check_collision(position1, position2):
    return position1 == position2

# Checking if snake is withing the board
def is_within_bounds(position, board_size):
    x, y = position
    width, height = board_size
    return 0 <= x < width and 0 <= y < height

# Increasing speed with score
def increase_speed(score):
    starting_speed = 1
    max_speed = 2
    current_speed = starting_speed + (score // 3) * 0.1
    return min(current_speed, max_speed)