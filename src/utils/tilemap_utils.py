import json
import pygame
from os import path

from const import SPRITESHEET_WIDTH
from utils.remove_file_extension import remove_file_extension


def tilemap_routine(
    tile_json_path: str, base_dir: str, current_stage: str, spritesheet: pygame.Surface
):
    # important! spritesheet must have 32 tiles per row or 512 x 512 px in size, this is by design for saving mem sake

    # prepare output
    tileheight = 0
    width = 0
    height = 0
    solid_layer_index = 0
    thin_layer_index = 0
    players = []
    enemies = []
    doors = []
    tile_sheet_name = ""

    # read json
    with open(tile_json_path, "r") as file:
        data = json.load(file)
        tileheight = data["tileheight"]
        width = data["width"]
        height = data["height"]
        tile_sheet_name = remove_file_extension(data["tilesets"][0]["source"])

    # if this json data has diff tile sheet, then we are entering a new stage room
    if current_stage != tile_sheet_name:
        print("switch stage!", current_stage, tile_sheet_name)
        # load new stage image, overwrite passed in spritesheet with new one
        spritesheet = pygame.image.load(
            path.join(base_dir, "pngs", f"{tile_sheet_name}.png")
        ).convert_alpha()

    # prepare pre rendered bg paper
    pre_rendered_bg: pygame.Surface = pygame.Surface(
        (width * tileheight, height * tileheight), pygame.SRCALPHA
    )

    # iter json
    for index, layer in enumerate(data["layers"]):
        # collect player positions (in a room there are finite possible pos a player starts in, left door, right door, etc...)
        # this is supposed to be "PlayerPositions", "Player" name is misleading but whatever la too lazy to change it
        if layer["name"] == "Player":
            for player in layer["objects"]:
                players.append(player)
        # collect enemies
        if layer["name"] == "Enemies":
            for enemy in layer["objects"]:
                enemies.append(enemy)
        # collect doors
        if layer["name"] == "Doors":
            for door in layer["objects"]:
                doors.append(door)
        # todo: collect item drop, save station, cutscene toggler, etc...

        # iter bg
        if not layer["type"] == "tilelayer":
            continue
        if layer["name"] == "Solid":
            solid_layer_index = index
        if layer["name"] == "Thin":
            thin_layer_index = index
        for index, tile_id in enumerate(layer["data"]):
            tile_id -= 1
            if tile_id == -1:
                continue
            # calc destination on world
            x = index % width
            y = index // width
            dest_x = x * tileheight
            dest_y = y * tileheight
            # get spritesheet region source position
            src_x = (tile_id % SPRITESHEET_WIDTH) * tileheight
            src_y = (tile_id // SPRITESHEET_WIDTH) * tileheight
            # start painting the pre rendered bg
            pre_rendered_bg.blit(
                spritesheet, (dest_x, dest_y), (src_x, src_y, tileheight, tileheight)
            )

    # get solid, thin and other static collidable / hitable things THAT DOES NOT HAVE DATA (like sticky floor, or slippery floor, but NOT ITEMS or DOORS)
    # cuz these are to hold id only, like oh im on id 2, that means its thin, then they do whatever they want with that info, like if its on id 2 and press jump we drop off of it
    collision_layer = "".join(
        "1"
        if data["layers"][solid_layer_index]["data"][y * width + x] != 0
        else "2"
        if data["layers"][thin_layer_index]["data"][y * width + x] != 0
        else "0"
        for y in range(height)
        for x in range(width)
    )

    return {
        "width": width,
        "height": height,
        "tileheight": tileheight,
        "collision_layer": collision_layer,
        "pre_rendered_bg": pre_rendered_bg,
        "players": players,
        "enemies": enemies,
        "doors": doors,
        "spritesheet": spritesheet,
        "tile_sheet_name": tile_sheet_name,
    }
