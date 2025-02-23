import pygame
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

# Constants
WIDTH, HEIGHT = 320, 180
FPS = 60
TILE_SIZE = 16

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

# Get first room
# todo: move player and enemies to room, make 1 room class per stages, each room will load its stage data once (enemy json, interactive json, etc)
room = Room(base_dir, "test_room.json", "forest_of_illusion_tile_sheet.png")

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
quad = quadtree_utils.QuadTree(pygame.FRect(0, 0, room.width * 16, room.height * 16))

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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                use_quadtree = not use_quadtree

        # Get key states
        keys = pygame.key.get_pressed()
        player.update(keys, dt)

        # update enemy type 1 collision layer
        quad.clear()
        for particle in particles:
            quad.insert(particle)

        # handle enemy type 1 bouncing off of each other
        for particle in particles:
            # reset bounce color
            particle.surf.fill(particle.colr)
            nearby = (
                quad.search(particle.rect)
                if use_quadtree
                else [
                    p
                    for p in particles
                    if p.rect.colliderect(particle.rect) and p != particle
                ]
            )
            for other in nearby:
                if other != particle:
                    particle.bounce_with(other)

        # use player rect to find nearby particles
        player.surf.fill("red")
        nearby = (
            quad.search(player.rect)
            if use_quadtree
            else [p for p in particles if p.rect.colliderect(player.rect)]
        )
        if len(nearby):
            player.surf.fill("yellow")

        camera.center = player.rect.center
        camera.clamp_ip(room.rect)

        # Draw
        screen.fill("black")
        # todo: draw the parallax stuff here
        screen.blit(room.pre_rendered_bg, (-camera.x, -camera.y))
        player.draw(screen, camera)

        # use cam rect to find nearby particle to draw and update them
        nearby = quad.search(camera) if use_quadtree else particles
        for particle in nearby:
            particle.update(dt)
            particle.draw(screen, camera)

        # Update the screen
        pygame.display.update()
        clock.tick(FPS)  # Cap the frame rate

    pygame.quit()


if __name__ == "__main__":
    main()
