from os import path

import pygame

# this will have to import all existing enemies in the game, also parallax bg and everything else, just store the class in a dict, not the intsance
from door import Door
from enemy_type_1 import EnemyType1
from player import Player
from utils import quadtree_utils
from utils.tilemap_utils import tilemap_routine
from const import HEIGHT, TILE_SIZE, WIDTH


class Room:
    # the idea is that when player hits door, just grab door room target json path, then re init this again, door should have target room player pos name too
    def __init__(self, base_dir, tile_json_path):
        # load this room sprite sheet
        # todo: load other data here if need be like enemy animation
        # todo: when stage change, we have to change the png and other json data here again
        # so make sure to have a dict that has key stage name then value dict that holds class mem ref or json or whatever to be loaded
        self.base_dir = base_dir

        # read json, this thing knows when stage change, so it will load only the needed anim json, or enemy png, that is tied to this stage
        data = tilemap_routine(
            path.join(self.base_dir, "jsons", tile_json_path),
            base_dir,
            current_stage="",
            spritesheet=None,
        )
        # set my props with json
        self.width = data["width"]
        self.height = data["height"]
        self.tileheight = data["tileheight"]
        self.collision_layer = data["collision_layer"]
        self.pre_rendered_bg = data["pre_rendered_bg"]
        self.players = data["players"]
        self.enemies = data["enemies"]
        self.raw_doors = data["doors"]
        # spritesheet name is stage name, 1 stage 1 spritesheet
        self.current_stage = data["tile_sheet_name"]
        self.spritesheet = data["spritesheet"]
        self.rect = pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)

        # player
        # hard code just get player 1st pos
        # todo: loop over room to find which pos to put player in (from door signal up on room switch)
        player_first_pos = self.players[0]
        # use the on door change room door name, to get the right pos
        self.player = Player(player_first_pos["x"], player_first_pos["y"], self)

        # spawn enemies
        # todo: next time dedicate 1 list and 1 collision layer per enemy
        self.enemy_type_1_list: list[EnemyType1] = []
        for enemy in self.enemies:
            # todo: make a new prop for me to bind enemy names to their json, the one that fills the json val is the tilemap routine
            # todo: use enemy name as key to grab which one to spawn, for now hardcode the 1 enemy that i have
            self.enemy_type_1_list.append(EnemyType1(enemy["x"], enemy["y"], self))

        # spawn doors
        self.doors: list[Door] = []
        for door in self.raw_doors:
            self.doors.append(
                Door(door["x"], door["y"], door["properties"][0]["value"], door["name"])
            )

        # enemy type 1 collision layer
        self.enemy_type_1_collision_layer = quadtree_utils.QuadTree(
            pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)
        )

        # door collision layer
        self.door_collision_layer = quadtree_utils.QuadTree(
            pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)
        )
        for door in self.doors:
            self.door_collision_layer.insert(door)

        # Camera viewport
        self.camera = pygame.FRect(0, 0, WIDTH, HEIGHT)

        # debug quad vs no quad
        self.use_quadtree = True

    def change_room(self, tile_json_path, target_door_name):
        # read new json
        data = tilemap_routine(
            path.join(self.base_dir, "jsons", tile_json_path),
            self.base_dir,
            self.current_stage,
            self.spritesheet,
        )
        # update my props with new json
        self.width = data["width"]
        self.height = data["height"]
        self.tileheight = data["tileheight"]
        self.collision_layer = data["collision_layer"]
        self.pre_rendered_bg = data["pre_rendered_bg"]
        self.players = data["players"]
        self.enemies = data["enemies"]
        self.raw_doors = data["doors"]
        # spritesheet name is stage name, 1 stage 1 spritesheet
        self.current_stage = data["tile_sheet_name"]
        self.spritesheet = data["spritesheet"]
        self.rect = pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)

        # player
        # hard code just get player 1st pos
        # todo: loop over room to find which pos to put player in (from door signal up on room switch)
        player_first_pos = self.players[0]
        for player in self.players:
            if player["name"] == target_door_name:
                player_first_pos = player
        # use the on door change room door name, to get the right pos
        self.player = Player(player_first_pos["x"], player_first_pos["y"], self)

        # spawn enemies
        # todo: next time dedicate 1 list and 1 collision layer per enemy
        self.enemy_type_1_list: list[EnemyType1] = []
        for enemy in self.enemies:
            # todo: use enemy name as key to grab which one to spawn, for now hardcode the 1 enemy that i have
            self.enemy_type_1_list.append(EnemyType1(enemy["x"], enemy["y"], self))

        # spawn doors
        self.doors: list[Door] = []
        for door in self.raw_doors:
            self.doors.append(
                Door(door["x"], door["y"], door["properties"][0]["value"], door["name"])
            )

        # enemy type 1 collision layer
        self.enemy_type_1_collision_layer = quadtree_utils.QuadTree(
            pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)
        )

        # door collision layer
        self.door_collision_layer = quadtree_utils.QuadTree(
            pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)
        )
        for door in self.doors:
            self.door_collision_layer.insert(door)

        # Camera viewport
        self.camera = pygame.FRect(0, 0, WIDTH, HEIGHT)

        # debug quad vs no quad
        self.use_quadtree = True

    def event(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            self.use_quadtree = not self.use_quadtree

    def update(self, dt: int, screen: pygame.Surface):
        # Get key states
        self.player.update(dt)

        # update door collision layer
        # no need to update door collision layer since doors are not moving

        # update enemy type 1 collision layer
        self.enemy_type_1_collision_layer.clear()
        for enemy_type_1 in self.enemy_type_1_list:
            self.enemy_type_1_collision_layer.insert(enemy_type_1)

            # handle enemy type 1 bouncing off of each other
            # reset bounce color
            enemy_type_1.surf.fill(enemy_type_1.colr)
            nearby = (
                self.enemy_type_1_collision_layer.search(enemy_type_1.rect)
                if self.use_quadtree
                else [
                    p
                    for p in self.enemy_type_1_list
                    if p.rect.colliderect(enemy_type_1.rect) and p != enemy_type_1
                ]
            )
            for other in nearby:
                if other != enemy_type_1:
                    enemy_type_1.bounce_with(other)

        # handle player hitting enemy type 1
        self.player.surf.fill("red")
        nearby = (
            self.enemy_type_1_collision_layer.search(self.player.rect)
            if self.use_quadtree
            else [
                p
                for p in self.enemy_type_1_list
                if p.rect.colliderect(self.player.rect)
            ]
        )
        if len(nearby):
            self.player.surf.fill("yellow")

        # handle player hitting door
        nearby = (
            self.door_collision_layer.search(self.player.rect)
            if self.use_quadtree
            else [p for p in self.doors if p.rect.colliderect(self.player.rect)]
        )
        if len(nearby):
            self.player.surf.fill("blue")
            self.change_room(nearby[0].target_room_json_name, nearby[0].name)

        # set cam to follow player
        # todo: use same move algo for cam later to follow player
        self.camera.center = self.player.rect.center
        self.camera.clamp_ip(self.rect)

        screen.fill("black")
        # todo: draw the parallax stuff here
        screen.blit(self.pre_rendered_bg, (-self.camera.x, -self.camera.y))
        self.player.draw(screen, self.camera)

        # handle update and draw enemy type 1 in cam
        nearby = (
            self.enemy_type_1_collision_layer.search(self.camera)
            if self.use_quadtree
            else self.enemy_type_1_list
        )
        for enemy_type_1 in nearby:
            enemy_type_1.update(dt)
            enemy_type_1.draw(screen, self.camera)

        # todo: remove this this is for debug only
        # handle update and draw door in cam
        nearby = (
            self.door_collision_layer.search(self.camera)
            if self.use_quadtree
            else self.doors
        )
        for door in nearby:
            door.draw(screen, self.camera)
