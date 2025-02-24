from os import path
import sys
import pygame
from const import FIRST_ROOM_JSON_NAME, FPS
from nodes.room import Room
from utils.init_pygame import init_pygame

# Get the main.py abs path in any machine!
base_dir = path.dirname(path.abspath(__file__))
if getattr(sys, "frozen", False):
    base_dir = path.dirname(sys.executable)

# Initialize Pygame
context = init_pygame()
screen = context.screen
clock = context.clock

# Get first game starting room
room = Room(base_dir, FIRST_ROOM_JSON_NAME)


def main():
    # Game Loop
    running = 1
    while running:
        dt = clock.tick(60)  # Cap at 60 FPS
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = 0

        # room update
        room.update(dt, screen)

        # Update the screen
        pygame.display.update()
        clock.tick(FPS)  # Cap the frame rate

    pygame.quit()


if __name__ == "__main__":
    main()
