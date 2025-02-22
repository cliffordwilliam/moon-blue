# A test run to see how to render from tiled
# Spritesheet must be 512x512 okay!

import pygame

import json
import os
import pygame

def tilemap_routine(tile_json_path: str, tile_png_path: str):
    # Get the path to the JSON file (os-agnostic)
    file_path = os.path.join(os.path.dirname(__file__), tile_json_path)
    tileheight = 0
    width = 0
    height = 0

    # Open the JSON file
    with open(file_path, 'r') as file:
        # Load the data from the JSON file
        data = json.load(file)
        tileheight = data['tileheight']
        width = data['width']
        height = data['height']

    pre_rendered_bg: pygame.Surface = pygame.Surface((width * tileheight, height * tileheight), pygame.SRCALPHA)

    # Load the spritesheet
    spritesheet_path = os.path.join(os.path.dirname(__file__), tile_png_path)
    spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

    # Generate world map grid (binary representation)
    world_map_grid_data = "".join(
        "1" if data['layers'][0]['data'][y * width + x] != 0 else "0"
        for y in range(height)
        for x in range(width)
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
            dest_x = x * tileheight
            dest_y = y * tileheight
            # Get spritesheet region source position
            src_x = (tile_id % 32) * tileheight  # Assuming spritesheet has 32 tiles per row
            src_y = (tile_id // 32) * tileheight
            pre_rendered_bg.blit(spritesheet, (dest_x, dest_y), (src_x, src_y, tileheight, tileheight))
    
    return {
        "width": width,
        "height": height,
        "tileheight": tileheight,
        "world_map_grid_data": world_map_grid_data,
        "pre_rendered_bg": pre_rendered_bg,
    }


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

data = tilemap_routine("test_room.json", "forest_of_illusion_tile_sheet.png")
width = data["width"]
height = data["height"]
tileheight = data["tileheight"]
world_map_grid_data = data["world_map_grid_data"]
pre_rendered_bg = data["pre_rendered_bg"]

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
