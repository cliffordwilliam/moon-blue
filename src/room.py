from os import path

import pygame

from utils.tilemap_utils import tilemap_routine


class Room:
    def __init__(self, base_dir, tile_json_path, tile_png_path):
        # read json
        data = tilemap_routine(
            path.join(base_dir, "jsons", tile_json_path),
            path.join(base_dir, "assets", tile_png_path),
        )
        # set my props with json
        self.width = data["width"]
        self.height = data["height"]
        self.tileheight = data["tileheight"]
        self.room_map_grid_data_solid = data["room_map_grid_data_solid"]
        self.room_map_grid_data_thin = data["room_map_grid_data_thin"]
        self.pre_rendered_bg = data["pre_rendered_bg"]
        self.players = data["players"]
        self.enemies = data["enemies"]
        self.rect = pygame.FRect(0, 0, self.width * 16, self.height * 16)
