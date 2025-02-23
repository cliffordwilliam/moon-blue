import json
import pygame


def tilemap_routine(tile_json_path: str, spritesheet: pygame.Surface):
    # prepare output
    tileheight = 0
    width = 0
    height = 0
    solid_layer_index = 0
    thin_layer_index = 0
    players = []
    enemies = []
    doors = []

    # read json
    with open(tile_json_path, "r") as file:
        data = json.load(file)
        tileheight = data["tileheight"]
        width = data["width"]
        height = data["height"]

    # prepare pre rendered bg paper
    pre_rendered_bg: pygame.Surface = pygame.Surface(
        (width * tileheight, height * tileheight), pygame.SRCALPHA
    )

    # spritesheet must have 32 tiles per row, 512 px in size
    spritesheet_width = 32

    # iter json
    for index, layer in enumerate(data["layers"]):
        # collect players (in a room there are finite possible pos a player starts in, left door, right door, etc...)
        if layer["name"] == "Player":
            for player in layer["objects"]:
                players.append(player)
        # collect enemies
        if layer["name"] == "Enemies":
            for enemy in layer["objects"]:
                enemies.append(enemy)
        # collect doors
        # todo: create new algo to instead create a string world map for doors just like solid and thin
        # todo: but if not then just treat doors like enemies its the same thing anyways
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
            src_x = (
                (tile_id % spritesheet_width) * tileheight
            )  # spritesheet must have 32 tiles per row, 512 px in size, for mem sake
            src_y = (tile_id // spritesheet_width) * tileheight
            pre_rendered_bg.blit(
                spritesheet, (dest_x, dest_y), (src_x, src_y, tileheight, tileheight)
            )

    # get solid, thin and other static collidable / hitable things like door
    room_map_grid_data_solid = "".join(
        "1" if data["layers"][solid_layer_index]["data"][y * width + x] != 0 else "0"
        for y in range(height)
        for x in range(width)
    )
    room_map_grid_data_thin = "".join(
        "1" if data["layers"][thin_layer_index]["data"][y * width + x] != 0 else "0"
        for y in range(height)
        for x in range(width)
    )

    return {
        "width": width,
        "height": height,
        "tileheight": tileheight,
        "room_map_grid_data_solid": room_map_grid_data_solid,
        "room_map_grid_data_thin": room_map_grid_data_thin,
        "pre_rendered_bg": pre_rendered_bg,
        "players": players,
        "enemies": enemies,
        "doors": doors,
    }
