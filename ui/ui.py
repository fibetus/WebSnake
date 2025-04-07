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

        # Set up the clock for snake moves
        clock = pygame.time.Clock()

        # Set up font for score
        font = pygame.font.SysFont(None, 36)

        # Game loop
        while True:
            current_time = pygame.time.get_ticks()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.game.change_direction("up")
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.game.change_direction("down")
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.game.change_direction("left")
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.game.change_direction("right")
                    elif event.key == pygame.K_r and self.game.game_over:
                        # Reset game
                        self.game.__init__(board_size=(self.grid_size, self.grid_size))
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

            # Update game state if game is not over and enough time has passed
            if not self.game.game_over:
                # Calculate time to wait based on game speed
                self.update_interval = int(1000 / self.game.speed)

                # Check if it's time to update
                if current_time - self.last_update_time >= self.update_interval:
                    self.game.update()
                    self.last_update_time = current_time

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

            # Game over text
            if self.game.game_over:
                # Semi-transparent overlay
                overlay = pygame.Surface((self.screen_width, self.screen_height))
                overlay.set_alpha(150)
                overlay.fill(self.BLACK)
                screen.blit(overlay, (0, 0))

                # Game over message
                game_over_text = font.render('GAME OVER!', True, self.WHITE)
                text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
                screen.blit(game_over_text, text_rect)

                # Restart instructions
                restart_text = font.render('Press R to restart or Q to quit', True, self.WHITE)
                restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
                screen.blit(restart_text, restart_rect)

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(60)


    def _draw_grid(self, screen):
        import pygame

        # Draw vertical lines
        for x in range(0, self.screen_width, self.cell_size):
            pygame.draw.line(screen, self.GRID_COLOR, (x, 0), (x, self.grid_size * self.cell_size))

        # Draw horizontal lines
        for y in range(0, self.grid_size * self.cell_size, self.cell_size):
            pygame.draw.line(screen, self.GRID_COLOR, (0, y), (self.screen_width, y))