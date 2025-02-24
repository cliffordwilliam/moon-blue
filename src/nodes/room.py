import copy
from os import path

import pygame

from const import HEIGHT, TILE_SIZE, WIDTH
from nodes.door import Door
from db.spritesheet_data_map import SpritesheetDataMap
from nodes.player import Player
from utils import quadtree_utils
from utils.tilemap_utils import tilemap_routine


class Room:
    def __init__(self, base_dir, tile_json_path):
        self.base_dir = base_dir
        self.spritesheet_data_map = SpritesheetDataMap(self.base_dir)
        self.spritesheet_instanced_data = {}
        self.camera = pygame.FRect(0, 0, WIDTH, HEIGHT)
        self._load_room_data(tile_json_path, "START")

    def on_player_hit_door_change_room(self, tile_json_path, target_door_name):
        self._load_room_data(tile_json_path, target_door_name)

    def update(self, dt: int, screen: pygame.Surface):
        self.player.update(dt)
        self.enemy_collision_layer.clear()

        for enemy in self.enemy_layer_list:
            self.enemy_collision_layer.insert(enemy)

        self.camera.center = self.player.rect.center
        self.camera.clamp_ip(self.rect)

        screen.fill("black")
        screen.blit(self.pre_rendered_bg, (-self.camera.x, -self.camera.y))
        self.player.draw(screen, self.camera)

        nearby_enemies = self.enemy_collision_layer.search(self.camera)
        for enemy in nearby_enemies:
            enemy.update(dt)
            enemy.draw(screen, self.camera)

    def _load_room_data(self, tile_json_path, target_door_name):
        data = tilemap_routine(
            path.join(self.base_dir, "jsons", tile_json_path),
            self.base_dir,
            current_stage=getattr(self, "current_stage", ""),
            spritesheet=getattr(self, "spritesheet", None),
        )

        self.width = data["width"]
        self.height = data["height"]
        self.tileheight = data["tileheight"]
        self.collision_layer = data["collision_layer"]
        self.pre_rendered_bg = data["pre_rendered_bg"]
        self.players = data["players"]
        self.enemies = data["enemies"]
        self.raw_doors = data["doors"]
        self.current_stage = data["tile_sheet_name"]
        self.spritesheet = data["spritesheet"]
        self.old_new_spritesheet = data["old_new_spritesheet"]
        self.rect = pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)

        if self.old_new_spritesheet["old"] != self.old_new_spritesheet["new"]:
            self.spritesheet_instanced_data = copy.deepcopy(
                self.spritesheet_data_map.spritesheet_data_map[
                    self.old_new_spritesheet["new"]
                ]
            )
            self.spritesheet_data_map.load_spritesheet_data(
                self.spritesheet_instanced_data
            )

        self.enemy_collision_layer = quadtree_utils.QuadTree(self.rect)
        self.enemy_layer_list = [
            self.spritesheet_instanced_data[enemy["name"]]["class_ref"](
                enemy["x"],
                enemy["y"],
                self,
                self.spritesheet_instanced_data[enemy["name"]]["png"],
                self.spritesheet_instanced_data[enemy["name"]]["json"],
                self.enemy_collision_layer,
            )
            for enemy in self.enemies
        ]

        self.door_collision_layer = quadtree_utils.QuadTree(self.rect)
        self.doors = [
            Door(door["x"], door["y"], door["properties"][0]["value"], door["name"])
            for door in self.raw_doors
        ]
        for door in self.doors:
            self.door_collision_layer.insert(door)

        self.player = Player(
            0,
            0,
            self,
            self.enemy_collision_layer,
            self.door_collision_layer,
        )
        for player in self.players:
            if player["name"] == target_door_name:
                self.player.rect.x = player["x"]
                self.player.rect.y = player["y"] - self.player.rect.h
                break
