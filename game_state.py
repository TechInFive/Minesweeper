
import math
import random
import time
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
RED = (255, 0, 0) 
DARK_GREEN = (0, 192, 0) 

background_color = GRAY
grid_color = LIGHT_GRAY
mine_color = BLACK

dark_edge_color = (128, 128, 128)
light_edge_color = WHITE
top_layer_color = (192, 192, 192)

font_size = 28

# Cell values
EMPTY = 'E'
MINE = 'M'

class Difficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

class CellState(Enum):
    HIDDEN = auto()
    REVEALED = auto()
    FLAGGED = auto()
    QUESTIONED = auto()

class GameStatus(Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    GAME_OVER = 2
    GAME_WIN = 3
    GAME_EXIT = 4

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
            settings = self.get_settings_by_difficulty(difficulty)
            self.cols = settings['cols']
            self.rows = settings['rows']
            self.total_mines = settings['mines']
            self.initialized = True

        self.grid = [
            [EMPTY for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        self.cell_state_grid = [
            [CellState.HIDDEN for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        self.place_mines_randomly()

        self.flags_placed = 0
        self.game_status = GameStatus.NOT_STARTED
        self.start_time = None
        self.elapsed_time = 0

    def get_settings_by_difficulty(self, difficulty):
        settings = {
            Difficulty.EASY: {'cols': 9, 'rows': 9, 'mines': 10},
            Difficulty.MEDIUM: {'cols': 16, 'rows': 16, 'mines': 40},
            Difficulty.HARD: {'cols': 30, 'rows': 16, 'mines': 99}
        }
        return settings.get(difficulty)

    def place_mines_randomly(self):
        possible_positions = [
            (x, y) for x in range(self.cols)
            for y in range(self.rows)
        ]

        mine_positions = set(random.sample(possible_positions, self.total_mines))
        for (x, y) in mine_positions:
            self.grid[y][x] = MINE
            # Increment hint numbers for adjacent cells
            for adj_y in range(max(0, y-1), min(self.rows, y+2)):
                for adj_x in range(max(0, x-1), min(self.cols, x+2)):
                    if self.grid[adj_y][adj_x] != MINE:
                        if self.grid[adj_y][adj_x] == EMPTY:
                            self.grid[adj_y][adj_x] = 1
                        else:
                            self.grid[adj_y][adj_x] += 1

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        
        if self.game_status in (GameStatus.GAME_OVER, GameStatus.GAME_WIN):
            if self.again_button_rect.collidepoint(event.pos):
                self.__init__(self.difficulty)
            elif self.menu_button_rect.collidepoint(event.pos):
                self.game_status = GameStatus.GAME_EXIT
        else:
            # Calculate grid position from mouse position
            x, y = event.pos
            grid_x = (x - left_span) // cell_size
            grid_y = (y - top_span) // cell_size
            
            # Ensure the click is within the grid bounds
            if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
                if event.button == 1:  # Left click
                    self.left_click_action(grid_x, grid_y)
                elif event.button == 3:  # Right click
                    self.right_click_action(grid_x, grid_y)

    def left_click_action(self, x, y):
        # Check if the cell is already revealed or flagged
        if self.cell_state_grid[y][x] in [CellState.REVEALED, CellState.FLAGGED]:
            return

        # Start timer for the first left click
        if self.game_status == GameStatus.NOT_STARTED:
            self.game_status = GameStatus.IN_PROGRESS
            self.start_time = time.time()

        if self.game_status != GameStatus.IN_PROGRESS:
            return

        # Check for game over
        if self.grid[y][x] == MINE:
            self.game_status = GameStatus.GAME_OVER

        # Use BFS to reveal surrounding cells if the clicked cell is empty
        queue = [(x, y)]
        while queue:
            current_x, current_y = queue.pop(0)
            self.cell_state_grid[current_y][current_x] = CellState.REVEALED

            if self.grid[current_y][current_x] != EMPTY:
                continue
            # Only check surrounding cells of an empty cell
            for adj_y in range(max(0, current_y-1), min(current_y+2, self.rows)):
                for adj_x in range(max(0, current_x-1), min(current_x+2, self.cols)):
                    if self.cell_state_grid[adj_y][adj_x] == CellState.HIDDEN:
                        queue.append((adj_x, adj_y))

        # Check for game win
        if all(self.cell_state_grid[y][x] != CellState.HIDDEN
               for x in range(self.cols)
               for y in range(self.rows)
               if self.grid[y][x] != MINE):
            self.game_status = GameStatus.GAME_WIN
    
    def right_click_action(self, x, y):
        current_state = self.cell_state_grid[y][x]
        if current_state == CellState.HIDDEN:
            self.cell_state_grid[y][x] = CellState.FLAGGED
            self.flags_placed += 1
        elif current_state == CellState.FLAGGED:
            self.cell_state_grid[y][x] = CellState.QUESTIONED
            self.flags_placed -= 1
        elif current_state == CellState.QUESTIONED:
            self.cell_state_grid[y][x] = CellState.HIDDEN

    def update(self):
        if self.game_status == GameStatus.IN_PROGRESS:
            self.elapsed_time = int(time.time() - self.start_time)

        if self.game_status == GameStatus.GAME_EXIT:
            return "menu"

    def reset_window(self):
        cols = self.cols
        rows = self.rows

        width = left_span + cols * cell_size + right_span
        height = rows * cell_size + top_span + bottom_span
        pygame.display.set_mode((width, height))

    def absolute_position(self, position):
        return (left_span + position[0] * cell_size, top_span + position[1] * cell_size)

    def draw_mine(self, screen, position):
        (x, y) = self.absolute_position(position)
        # Central point of the mine
        mine_center = (x + cell_size // 2, y + cell_size // 2)
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

    def draw_hint(self, screen, position, number):
        (x, y) = self.absolute_position(position)
        font = pygame.font.SysFont(None, font_size)
        text = font.render(str(number), True, BLACK)
        text_rect = text.get_rect(center=((x + cell_size // 2), (y + cell_size // 2)))
        screen.blit(text, text_rect)

    def draw_flag(self, screen, position):
        (x, y) = self.absolute_position(position)
        # Pole
        pygame.draw.line(screen, BLACK, (x + cell_size // 2, y + cell_size // 4),
                         (x + cell_size // 2, y + 3 * cell_size // 4), 2)
        # Flag
        pygame.draw.polygon(screen, RED, [(x + cell_size // 2 + 1, y + cell_size // 4),
                                          (x + cell_size - 5, y + cell_size // 2),
                                          (x + cell_size // 2 + 1, y + cell_size // 2)])

    def draw_question_mark(self, screen, position):
        (x, y) = self.absolute_position(position)
        font = pygame.font.SysFont(None, font_size)
        text = font.render('?', True, BLACK)
        text_rect = text.get_rect(center=((x + cell_size // 2 + 1), (y + cell_size // 2)))
        screen.blit(text, text_rect)

    def draw_cover(self, screen, position):
        (x, y) = self.absolute_position(position)
        cell_rect = pygame.Rect(x + 1, y + 1, cell_size - 2, cell_size - 2)

        # Draw unrevealed cell with a 3D effect
        pygame.draw.rect(screen, top_layer_color, cell_rect)
        pygame.draw.line(screen, light_edge_color, cell_rect.topleft, cell_rect.bottomleft)
        pygame.draw.line(screen, light_edge_color, cell_rect.topleft, cell_rect.topright)
        pygame.draw.line(screen, dark_edge_color, cell_rect.bottomleft, cell_rect.bottomright)
        pygame.draw.line(screen, dark_edge_color, cell_rect.bottomright, cell_rect.topright)

    def draw_counter(self, screen):
        remaining_mines = self.total_mines - self.flags_placed
        counter_font = pygame.font.SysFont('digital', 30)  # Use a digital-looking font
        counter_surface = counter_font.render(f"{remaining_mines}", True, RED)
        screen.blit(counter_surface, (left_span, 10))  # Adjust position as needed

    def draw_timer(self, screen):
        timer_font = pygame.font.SysFont('digital', 30)
        timer_surface = timer_font.render(f"{self.elapsed_time}", True, RED)
        screen.blit(timer_surface, (screen.get_width() - timer_surface.get_width() - left_span , 10 ))

    def draw_buttons(self, screen):
        if self.game_status not in [GameStatus.GAME_OVER, GameStatus.GAME_WIN]:
            return

        font = pygame.font.SysFont('Arial', 14)
        font_color = RED if self.game_status == GameStatus.GAME_OVER else DARK_GREEN
        play_again_render = font.render("Again", True, font_color)

        center_x = screen.get_width() / 2
        text_span = 2
        button_width = play_again_render.get_width() + text_span * 2
        button_height = play_again_render.get_height() + text_span * 2
        left_x = center_x - button_width - text_span
        self.again_button_rect = pygame.Rect(left_x, 10, button_width, button_height)
        pygame.draw.rect(screen, top_layer_color, self.again_button_rect)
        screen.blit(play_again_render, (left_x + text_span, 10 + text_span))

        menu_render = font.render("Menu", False, BLACK)
        button_width = menu_render.get_width() + text_span * 2
        self.menu_button_rect = pygame.Rect(center_x + text_span, 10, button_width, button_height)
        pygame.draw.rect(screen, top_layer_color, self.menu_button_rect)
        screen.blit(menu_render, (center_x + text_span, 10 + text_span))

    def draw(self, screen):
        # Clear the screen with a background color
        screen.fill(background_color)

        # Retrieve the the number of columns and rows
        cols = self.cols
        rows = self.rows

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

        # Draw mines and hints
        for y in range(self.rows):
            for x in range(self.cols):
                cell_state = self.cell_state_grid[y][x]
                if cell_state == CellState.REVEALED:
                    if self.grid[y][x] == MINE:
                        self.draw_mine(screen, (x, y))
                    elif self.grid[y][x] == EMPTY:
                        pass
                    else:
                        self.draw_hint(screen, (x, y), self.grid[y][x])
                elif cell_state == CellState.QUESTIONED:
                    self.draw_cover(screen, (x, y))
                    self.draw_question_mark(screen, (x, y))
                elif cell_state == CellState.FLAGGED:
                    self.draw_cover(screen, (x, y))
                    self.draw_flag(screen, (x, y))
                elif cell_state == CellState.HIDDEN:
                    self.draw_cover(screen, (x, y))

        self.draw_counter(screen)
        self.draw_timer(screen)
        self.draw_buttons(screen)

        # Update the display
        pygame.display.flip()
