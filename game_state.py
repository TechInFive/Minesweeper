
import math
import random
import pygame

from enum import Enum, auto

cell_size = 25

top_span = 40
bottom_span = 10
left_span = 10
right_span = 10

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (96, 96, 96)
GRAY = (224, 224, 224)

background_color = GRAY
grid_color = LIGHT_GRAY
mine_color = BLACK

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

        self.mine_positions = set()
        self.place_mines_randomly()

    def get_settings_by_difficulty(self, difficulty):
        settings = {
            Difficulty.EASY: {'cols': 9, 'rows': 9, 'mines': 10},
            Difficulty.MEDIUM: {'cols': 16, 'rows': 16, 'mines': 40},
            Difficulty.HARD: {'cols': 30, 'rows': 16, 'mines': 99}
        }
        return settings.get(difficulty)

    def place_mines_randomly(self):
        mines_to_place = self.settings['mines']

        possible_positions = [
            (x, y) for x in range(self.settings['cols'])
            for y in range(self.settings['rows'])
        ]

        self.mine_positions = set(random.sample(possible_positions, mines_to_place))

    def handle_event(self, event):
        # Handle game inputs (mouse clicks for revealing cells, flagging mines, etc.)
        pass

    def update(self):
        # Update game logic (check for win/lose, reveal cells, etc.)
        # Return to MenuState or end the game based on game conditions
        pass

    def reset_window(self):
        cols = self.settings['cols']
        rows = self.settings['rows']

        width = left_span + cols * cell_size + right_span
        height = rows * cell_size + top_span + bottom_span
        pygame.display.set_mode((width, height))


    def draw_mine(self, screen, position):
        # Central point of the mine
        mine_center = (left_span + position[0] * cell_size + cell_size // 2,
                       top_span + position[1] * cell_size + cell_size // 2)
        mine_radius = cell_size // 4  # Radius of the mine circle

        # Draw the central mine circle
        pygame.draw.circle(screen, mine_color, mine_center, mine_radius)

        # Draw the spikes
        num_spikes = 8
        for i in range(num_spikes):
            angle = (360 / num_spikes) * i
            end_x = mine_center[0] + int(mine_radius * 1.5 * math.cos(math.radians(angle)))
            end_y = mine_center[1] + int(mine_radius * 1.5 * math.sin(math.radians(angle)))
            pygame.draw.line(screen, mine_color, mine_center, (end_x, end_y), 2)

    def draw(self, screen):
        # Clear the screen with a background color
        screen.fill(background_color)

        # Retrieve the the number of columns and rows
        cols = self.settings['cols']
        rows = self.settings['rows']

        right_x = left_span + cell_size * cols
        bottom_y = top_span + cell_size * rows

        # Draw the vertical lines
        for col in range(cols + 1):
            x = left_span + col * cell_size
            pygame.draw.line(screen, grid_color, (x, top_span), (x, bottom_y))

        # Draw the horizontal lines
        for row in range(rows + 1):
            y = top_span + row * cell_size
            pygame.draw.line(screen, grid_color, (left_span, y), (right_x, y))

        # Draw mines
        for pos in self.mine_positions:
            self.draw_mine(screen, pos)

        # Update the display
        pygame.display.flip()
