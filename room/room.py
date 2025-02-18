# A test run to see how to render from tiled
# Spritesheet must be 512x512 okay!

import json
import os
import pygame

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 320, 180
FPS = 60
TILE_SIZE = 16

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

# Data from json
tileheight = 0
width = 0
height = 0

# Get the path to the JSON file (os-agnostic)
file_path = os.path.join(os.path.dirname(__file__), 'test.json')

# Open the JSON file
with open(file_path, 'r') as file:
    # Load the data from the JSON file
    data = json.load(file)
    tileheight = data['tileheight']
    width = data['width']
    height = data['height']

# Prepare pre-rendered background
pre_rendered_bg: pygame.Surface = pygame.Surface((width * tileheight, height * tileheight))

# Load the spritesheet
spritesheet_path = os.path.join(os.path.dirname(__file__), 'forest_of_illusion_tile_sheet.png')
spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

# Generate world map grid (binary representation)
world_map_grid_data = "\n".join(
    "".join("1" if data['layers'][0]['data'][y * width + x] != 0 else "0" for x in range(width))
    for y in range(height)
)

# Iterate through the JSON data and render tiles
for layer in data['layers']:
    for index, tile_id in enumerate(layer['data']):
        tile_id -= 1
        if tile_id == -1:
            continue
        # Compute destination on world
        x = index % width
        y = index // width
        dest_x = x * TILE_SIZE
        dest_y = y * TILE_SIZE
        # Get spritesheet region source position
        src_x = (tile_id % 32) * TILE_SIZE  # Assuming spritesheet has 32 tiles per row
        src_y = (tile_id // 32) * TILE_SIZE
        pre_rendered_bg.blit(spritesheet, (dest_x, dest_y), (src_x, src_y, TILE_SIZE, TILE_SIZE))

# Game Loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the pre-rendered background
    screen.blit(pre_rendered_bg, (0, 0))

    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)  # Cap the frame rate

pygame.quit()
