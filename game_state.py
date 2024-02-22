
import pygame

from enum import Enum, auto

CELL_SIZE = 25

TOP_SPAN = 40
BOTTOM_SPAN = 10
LEFT_SPAN = 10
RIGHT_SPAN = 10

class Difficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

class GameState:
    instances = {}  # Class variable to store instances

    def __new__(cls, difficulty):
        if difficulty not in cls.instances:
            instance = super(GameState, cls).__new__(cls)
            cls.instances[difficulty] = instance
        return cls.instances[difficulty]

    def __init__(self, difficulty):
        if not hasattr(self, 'initialized'):  # Avoid reinitialization
            self.difficulty = difficulty
            self.settings = self.get_settings_by_difficulty(difficulty)
            self.initialized = True

    def get_settings_by_difficulty(self, difficulty):
        settings = {
            Difficulty.EASY: {'size': (9, 9), 'mines': 10},
            Difficulty.MEDIUM: {'size': (16, 16), 'mines': 40},
            Difficulty.HARD: {'size': (30, 16), 'mines': 99}
        }
        return settings.get(difficulty)

    def handle_event(self, event):
        # Handle game inputs (mouse clicks for revealing cells, flagging mines, etc.)
        pass

    def update(self):
        # Update game logic (check for win/lose, reveal cells, etc.)
        # Return to MenuState or end the game based on game conditions
        pass

    def reset_window(self):
        size = self.settings['size']
        width = LEFT_SPAN + size[0] * CELL_SIZE + RIGHT_SPAN
        height = size[1] * CELL_SIZE + TOP_SPAN + BOTTOM_SPAN
        pygame.display.set_mode((width, height))

    def draw(self, screen):
        # Clear the screen with a background color
        screen.fill((255, 255, 255))

        # Grid color
        grid_color = (0, 0, 0)

        # Retrieve the size of the game window and the number of columns and rows
        cols = self.settings['size'][0]
        rows = self.settings['size'][1]

        right_x = LEFT_SPAN + CELL_SIZE * cols
        bottom_y = TOP_SPAN + CELL_SIZE * rows

        # Draw the vertical lines
        for col in range(cols + 1):
            x = LEFT_SPAN + col * CELL_SIZE
            pygame.draw.line(screen, grid_color, (x, TOP_SPAN), (x, bottom_y))

        # Draw the horizontal lines
        for row in range(rows + 1):
            y = TOP_SPAN + row * CELL_SIZE
            pygame.draw.line(screen, grid_color, (LEFT_SPAN, y), (right_x, y))

        # Update the display
        pygame.display.flip()
