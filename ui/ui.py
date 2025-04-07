import pygame
import sys
import time

class UI:
    def __init__(self, game):

        self.game = game

        # Grid setup
        self.grid_size = 10  # 10x10 grid
        self.cell_size = 50  # Size of each cell in pixels

        # Window size based on grid
        self.screen_width = self.grid_size * self.cell_size
        self.screen_height = self.grid_size * self.cell_size + 50  # Extra space for score

        # Update timing
        self.last_update_time = 0
        self.update_interval = 1000  # milliseconds (will be adjusted by game speed)

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRID_COLOR = (40, 40, 40)

    def start(self):


        # Initialize Pygame
        pygame.init()

        # Set up the display
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Snake Game')


        # Set up font for score
        font = pygame.font.SysFont(None, 36)

        # Game loop
        while True:
            # Fill the screen with black
            screen.fill(self.BLACK)

            # Draw the grid
            self._draw_grid(screen)

            # Draw the snake
            for segment in self.game.snake:
                x, y = segment
                # Convert grid coordinates to pixel coordinates
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(screen, self.GREEN, rect)

                # Draw a darker border for the snake segment
                pygame.draw.rect(screen, (0, 200, 0), rect, 1)

            # Draw the food
            fx, fy = self.game.food
            food_rect = pygame.Rect(
                fx * self.cell_size,
                fy * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(screen, self.RED, food_rect)

            # Draw score
            score_text = font.render(f'Score: {self.game.score}', True, self.WHITE)
            screen.blit(score_text, (10, self.grid_size * self.cell_size + 10))

            # Draw speed info
            speed_text = font.render(f'Speed: {self.game.speed:.1f}x', True, self.WHITE)
            speed_rect = speed_text.get_rect()
            speed_rect.right = self.screen_width - 10
            speed_rect.top = self.grid_size * self.cell_size + 10
            screen.blit(speed_text, speed_rect)

            # Update the display
            pygame.display.flip()


    def _draw_grid(self, screen):
        import pygame

        # Draw vertical lines
        for x in range(0, self.screen_width, self.cell_size):
            pygame.draw.line(screen, self.GRID_COLOR, (x, 0), (x, self.grid_size * self.cell_size))

        # Draw horizontal lines
        for y in range(0, self.grid_size * self.cell_size, self.cell_size):
            pygame.draw.line(screen, self.GRID_COLOR, (0, y), (self.screen_width, y))