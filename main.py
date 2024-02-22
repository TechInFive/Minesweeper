import pygame
import sys

from menu_state import MenuState
from game_state import GameState

def main():
    pygame.init()

    # Initial state
    current_state = MenuState()

    screen = current_state.reset_window()
    pygame.display.set_caption("Minesweeper")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Pass the event to the current state for processing
            current_state.handle_event(event)

        # Update the current state and check for state change
        next_state = current_state.update()
        if next_state is not None:
            if isinstance(next_state, MenuState):
                current_state = MenuState()
            elif isinstance(next_state, GameState):
                current_state = next_state

        # Draw the current state
        current_state.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
