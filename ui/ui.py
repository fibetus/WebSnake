import pygame
import sys
import time
from engine import Game


class UI:
    def __init__(self, game=None):
        # Setup pygame
        pygame.init()
        pygame.font.init()

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRID_COLOR = (40, 40, 40)
        self.BUTTON_COLOR = (100, 100, 200)
        self.BUTTON_HOVER_COLOR = (120, 120, 220)

        # Default screen size for setup
        self.screen_width = 500
        self.screen_height = 550

        # Default font
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # Game instance
        self.game = game

        # Player data
        self.player_name = ""
        self.player_data = None

        # Grid setup (will be configured during setup)
        self.grid_size = 10
        self.cell_size = 50

        # Update timing
        self.last_update_time = 0
        self.update_interval = 1000  # milliseconds (will be adjusted by game speed)

        # Text input variables
        self.active_input = None
        self.input_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0

    def show_setup_scene(self, player_data):
        self.player_data = player_data
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Snake Game - Setup')

        # Default values
        self.grid_size = 10
        input_rect = pygame.Rect(150, 250, 200, 32)
        slider_rect = pygame.Rect(150, 350, 200, 10)
        slider_button_rect = pygame.Rect(150 + (self.grid_size - 5) * 10, 345, 20, 20)

        start_button = pygame.Rect(150, 450, 200, 50)

        clock = pygame.time.Clock()

        # Input fields active state
        name_input_active = False
        slider_active = False

        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Mouse click handling
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if name input field clicked
                    if input_rect.collidepoint(event.pos):
                        name_input_active = True
                    else:
                        name_input_active = False

                    # Check if slider is clicked
                    if slider_button_rect.collidepoint(event.pos) or slider_rect.collidepoint(event.pos):
                        slider_active = True
                    else:
                        slider_active = False

                    # Check if start button is clicked
                    if start_button.collidepoint(event.pos) and self.player_name.strip():
                        # Create and start game with selected parameters
                        self.setup_game()
                        return

                # Mouse button release
                if event.type == pygame.MOUSEBUTTONUP:
                    slider_active = False

                # Mouse drag for slider
                if event.type == pygame.MOUSEMOTION and slider_active:
                    # Update grid size based on slider position
                    x_pos = max(slider_rect.left, min(slider_rect.right, mouse_pos[0]))
                    rel_pos = (x_pos - slider_rect.left) / slider_rect.width
                    self.grid_size = max(5, min(25, int(5 + rel_pos * 20)))
                    slider_button_rect.x = slider_rect.left + (self.grid_size - 5) * 10

                # Keyboard input for name
                if event.type == pygame.KEYDOWN:
                    if name_input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif event.key == pygame.K_RETURN:
                            name_input_active = False
                        elif len(self.player_name) < 10:  # Limit name length
                            if event.unicode.isalnum() or event.unicode.isspace():
                                self.player_name += event.unicode

            # Clear screen
            screen.fill(self.BLACK)

            # Draw title
            title_text = self.font.render('Snake Game Setup', True, self.WHITE)
            screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 50))

            # Draw name input field
            name_color = self.WHITE if name_input_active else self.GRID_COLOR
            pygame.draw.rect(screen, name_color, input_rect, 2)

            # Draw name label
            name_label = self.font.render('Your Name:', True, self.WHITE)
            screen.blit(name_label, (150, 220))

            # Draw name text
            name_surf = self.font.render(self.player_name, True, self.WHITE)
            screen.blit(name_surf, (input_rect.x + 5, input_rect.y + 5))

            # Draw cursor if input is active
            if name_input_active and self.cursor_visible:
                cursor_x = input_rect.x + 5 + name_surf.get_width()
                pygame.draw.line(screen, self.WHITE,
                                 (cursor_x, input_rect.y + 5),
                                 (cursor_x, input_rect.y + 27), 2)

            # Draw grid size selector label
            size_label = self.font.render(f'Grid Size: {self.grid_size}x{self.grid_size}', True, self.WHITE)
            screen.blit(size_label, (150, 320))

            # Draw slider
            pygame.draw.rect(screen, self.WHITE, slider_rect)

            # Draw slider button
            slider_button_color = self.GREEN if slider_active else self.BUTTON_COLOR
            pygame.draw.rect(screen, slider_button_color, slider_button_rect)

            # Draw min/max labels
            min_label = self.small_font.render('5x5', True, self.WHITE)
            screen.blit(min_label, (slider_rect.left - 30, slider_rect.y - 5))

            max_label = self.small_font.render('25x25', True, self.WHITE)
            screen.blit(max_label, (slider_rect.right + 5, slider_rect.y - 5))

            # Draw start button
            button_color = self.BUTTON_HOVER_COLOR if start_button.collidepoint(mouse_pos) else self.BUTTON_COLOR
            pygame.draw.rect(screen, button_color, start_button)

            # Draw button text
            button_text = self.font.render('Start Game', True, self.WHITE)
            text_rect = button_text.get_rect(center=start_button.center)
            screen.blit(button_text, text_rect)

            # Draw instruction if name is empty
            if not self.player_name.strip():
                instruction = self.small_font.render('Please enter your name to start', True, self.RED)
                screen.blit(instruction, (150, 290))

            # Update cursor visibility (blinking effect)
            if pygame.time.get_ticks() - self.cursor_timer > 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = pygame.time.get_ticks()

            pygame.display.flip()
            clock.tick(60)

    def setup_game(self):
        """Set up the game based on user selections"""
        # Calculate cell size based on screen dimensions and grid size
        self.cell_size = min(500 // self.grid_size, 50)  # Max cell size of 50px

        # Update screen dimensions
        self.screen_width = self.grid_size * self.cell_size
        self.screen_height = self.grid_size * self.cell_size + 50  # Extra space for score

        # Create new game with selected size
        self.game = Game(
            board_size=(self.grid_size, self.grid_size),
            initial_position=(self.grid_size // 2, self.grid_size // 2),
            direction="right"
        )

        # Store player info
        if self.player_data:
            self.player_data.add_player(self.player_name)

    def start(self):
        """Start the main game loop"""
        if not self.game:
            raise ValueError("Game must be set up before starting")

        # Set up the display
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(f'Snake Game - {self.player_name}')

        # Set up the clock for snake moves
        clock = pygame.time.Clock()

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

            # Adjust font size for score and player name based on screen width
            font_size = max(24, min(36, int(self.screen_width / 15)))
            game_info_font = pygame.font.SysFont(None, font_size)

            # Draw score with adjusted font
            score_text = game_info_font.render(f'Score: {self.game.score}', True, self.WHITE)
            screen.blit(score_text, (10, self.grid_size * self.cell_size + 10))

            # Draw player name with adjusted font
            player_text = game_info_font.render(f'Player: {self.player_name}', True, self.WHITE)
            player_rect = player_text.get_rect()
            player_rect.right = self.screen_width - 10
            player_rect.top = self.grid_size * self.cell_size + 10
            screen.blit(player_text, player_rect)

            # Game over text
            if self.game.game_over:
                # Update player score if game is over
                if self.player_data:
                    # Update the player's score in the player data
                    for player in self.player_data.players:
                        if player["name"] == self.player_name:
                            player["score"] = max(player["score"], self.game.score)
                            break

                # Semi-transparent overlay
                overlay = pygame.Surface((self.screen_width, self.screen_height))
                overlay.set_alpha(150)
                overlay.fill(self.BLACK)
                screen.blit(overlay, (0, 0))

                # Game over message
                game_over_text = self.font.render('GAME OVER!', True, self.WHITE)
                text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
                screen.blit(game_over_text, text_rect)

                # Adjust font size for restart instructions based on screen width
                font_size = max(14, min(36, int(self.screen_width / 15)))
                restart_font = pygame.font.SysFont(None, font_size)

                # Restart instructions with adjusted font
                restart_text = restart_font.render('Press R to restart or Q to quit', True, self.WHITE)
                restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
                screen.blit(restart_text, restart_rect)

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(60)

    def _draw_grid(self, screen):
        # Draw vertical lines
        for x in range(0, self.screen_width, self.cell_size):
            pygame.draw.line(screen, self.GRID_COLOR, (x, 0), (x, self.grid_size * self.cell_size))

        # Draw horizontal lines
        for y in range(0, self.grid_size * self.cell_size, self.cell_size):
            pygame.draw.line(screen, self.GRID_COLOR, (0, y), (self.screen_width, y))