import pygame

from game_state import Difficulty, GameState

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Define button properties
button_color = GRAY
button_hover_color = (150, 150, 150)
text_color = BLACK
button_width = 200
button_height = 50

class Button:
    def __init__(self, x, y, width, height, text, difficulty):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = button_color
        self.difficulty = difficulty

    def draw(self, screen, mouse):
        if self.rect.collidepoint(mouse):
            self.color = button_hover_color
        else:
            self.color = button_color

        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.SysFont(None, 40)
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class MenuState:
    def __init__(self):
        # Initialize menu components
        self.buttons = [
            Button(200, 200, button_width, button_height, 'Easy', Difficulty.EASY),
            Button(200, 300, button_width, button_height, 'Medium', Difficulty.MEDIUM),
            Button(200, 400, button_width, button_height, 'Hard', Difficulty.HARD)
        ]
        self.next_state = None

    def handle_event(self, event):
        # Handle user inputs to select difficulty
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for button in self.buttons:
                if button.is_clicked(mouse_pos):
                    self.next_state = GameState(button.difficulty)  # Get singleton instance
                    self.next_state.reset_window()
        pass

    def reset_window(self):
        return pygame.display.set_mode((600, 600))

    def update(self):
        # Return GameState object when user makes a selection
        return self.next_state

    def draw(self, screen):
        # Draw the menu on the screen
        screen.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.draw(screen, mouse_pos)
