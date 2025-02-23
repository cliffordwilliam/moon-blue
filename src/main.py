import pygame
from const import FPS, HEIGHT, WIDTH
from room import Room
from os import path
import sys


# Get the main.py abs path in any machine!
base_dir = path.dirname(path.abspath(__file__))
if getattr(sys, "frozen", False):
    base_dir = path.dirname(sys.executable)

# Initialize Pygame
pygame.init()

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

# Get first room
# todo: move player and enemies to room, make 1 room class per stages, each room will load its stage data once (enemy json, interactive json, etc)
room = Room(base_dir, "test_room.json")


def main():
    # Game Loop
    running = True
    while running:
        dt = clock.tick(60)  # Cap at 60 FPS
        pygame.display.set_caption(
            f"Iteration Time: {dt} ms | Quadtree: {'ON' if room.use_quadtree else 'OFF'}"
        )
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # room event
            room.event(event)

        # room update
        room.update(dt, screen)

        # Update the screen
        pygame.display.update()
        clock.tick(FPS)  # Cap the frame rate

    pygame.quit()


if __name__ == "__main__":
    main()
