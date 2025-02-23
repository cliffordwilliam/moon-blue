from os import path

import pygame

# this will have to import all existing enemies in the game, also parallax bg and everything else, just store the class in a dict, not the intsance
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
        spritesheet = pygame.image.load(
            path.join(base_dir, "pngs", "forest_of_illusion_tile_sheet.png")
        ).convert_alpha()

        # read json
        data = tilemap_routine(
            path.join(base_dir, "jsons", tile_json_path),
            spritesheet,
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
        self.rect = pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)

        # player
        # hard code just get player 1st pos
        # todo: loop over room to find which pos to put player in (from door signal up on room switch)
        player_first_pos = self.players[0]
        self.player = Player(player_first_pos["x"], player_first_pos["y"], self)

        # spawn enemies
        self.particles: list[EnemyType1] = []
        for enemy in self.enemies:
            # todo: use enemy name as key to grab which one to spawn, for now hardcode the 1 enemy that i have
            self.particles.append(EnemyType1(enemy["x"], enemy["y"], self))

        # enemy type 1 collision layer
        self.quad = quadtree_utils.QuadTree(
            pygame.FRect(0, 0, self.width * TILE_SIZE, self.height * TILE_SIZE)
        )

        # Camera viewport
        self.camera = pygame.FRect(0, 0, WIDTH, HEIGHT)

        # debug quad vs no quad
        self.use_quadtree = True

    def event(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            self.use_quadtree = not self.use_quadtree

    def update(self, dt: int, screen: pygame.Surface):
        # Get key states
        keys = pygame.key.get_pressed()
        self.player.update(keys, dt)

        # update enemy type 1 collision layer
        self.quad.clear()
        for particle in self.particles:
            self.quad.insert(particle)

            # handle enemy type 1 bouncing off of each other
            # reset bounce color
            particle.surf.fill(particle.colr)
            nearby = (
                self.quad.search(particle.rect)
                if self.use_quadtree
                else [
                    p
                    for p in self.particles
                    if p.rect.colliderect(particle.rect) and p != particle
                ]
            )
            for other in nearby:
                if other != particle:
                    particle.bounce_with(other)

        # handle player hitting enemy type 1
        self.player.surf.fill("red")
        nearby = (
            self.quad.search(self.player.rect)
            if self.use_quadtree
            else [p for p in self.particles if p.rect.colliderect(self.player.rect)]
        )
        if len(nearby):
            self.player.surf.fill("yellow")

        # set cam to follow player
        # todo: use same move algo for cam later to follow player
        self.camera.center = self.player.rect.center
        self.camera.clamp_ip(self.rect)

        screen.fill("black")
        # todo: draw the parallax stuff here
        screen.blit(self.pre_rendered_bg, (-self.camera.x, -self.camera.y))
        self.player.draw(screen, self.camera)

        # handle update and draw enemy type 1 in cam
        nearby = self.quad.search(self.camera) if self.use_quadtree else self.particles
        for particle in nearby:
            particle.update(dt)
            particle.draw(screen, self.camera)
