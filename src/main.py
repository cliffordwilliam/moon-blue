import pygame
from const import FPS, HEIGHT, TILE_SIZE, WIDTH
from enemy_type_1 import EnemyType1
from player import Player
from room import Room
from os import path
import sys

from utils import quadtree_utils

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

# hard code just get player 1st pos
# todo: loop over room to find which pos to put player in (from door signal up on room switch)
player_first_pos = room.players[0]
player = Player(player_first_pos["x"], player_first_pos["y"], room)

# spawn enemies
particles: list[EnemyType1] = []
for enemy in room.enemies:
    # todo: use enemy name as key to grab which one to spawn, for now hardcode the 1 enemy that i have
    particles.append(EnemyType1(enemy["x"], enemy["y"], room))

# enemy type 1 collision layer
quad = quadtree_utils.QuadTree(
    pygame.FRect(0, 0, room.width * TILE_SIZE, room.height * TILE_SIZE)
)

# Camera viewport
camera = pygame.FRect(0, 0, WIDTH, HEIGHT)


def main():
    use_quadtree = True
    # Game Loop
    running = True
    while running:
        dt = clock.tick(60)  # Cap at 60 FPS
        pygame.display.set_caption(
            f"Iteration Time: {dt} ms | Quadtree: {'ON' if use_quadtree else 'OFF'}"
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
