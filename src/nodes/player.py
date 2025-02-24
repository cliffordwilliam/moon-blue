import pygame

# from room import Room
from utils import raycast_utils


class Player:
    def __init__(self, x, y, room, enemy_collision_layer, door_collision_layer):
        # player needs room ref, for move and slide and pos clamping within room limit
        self.room = room
        self.surf: pygame.Surface = pygame.Surface((7, 18))
        self.surf.fill("red")
        self.rect: pygame.FRect = self.surf.get_frect()
        # set pos is by rect bottom left
        self.rect.x = x
        self.rect.y = y - self.rect.h

        self.max_run: float = 0.09  # Px / ms
        self.velocity: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
        self.decay: float = 0.01
        self.floor = ""

        self.enemy_collision_layer = enemy_collision_layer
        self.door_collision_layer = door_collision_layer

    def update(self, dt):
        pressed = pygame.key.get_pressed()
        just_pressed = pygame.key.get_just_pressed()
        # Get dir
        direction_horizontal = pressed[pygame.K_RIGHT] - pressed[pygame.K_LEFT]
        direction_vertical = pressed[pygame.K_DOWN] - pressed[pygame.K_UP]
        # Update vel with dir
        self.velocity.x = raycast_utils.exp_decay(
            self.velocity.x, direction_horizontal * self.max_run, self.decay, dt
        )
        self.velocity.y = raycast_utils.exp_decay(
            self.velocity.y, direction_vertical * self.max_run, self.decay, dt
        )
        # Move and slide just like in Godot
        contact_normal = pygame.Vector2(0.0, 0.0)
        contact_point = pygame.Vector2(0.0, 0.0)
        tile_you_hit = raycast_utils.resolve_vel_against_solid_tiles(
            self.rect,
            dt,
            self.velocity,
            self.room.tileheight,
            self.room.width,
            self.room.height,
            self.room.collision_layer,
            contact_point,
            contact_normal,
            is_player=True,
        )
        if contact_normal.y == -1:
            self.floor = tile_you_hit
        # Update pos
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        # Clamp in screen rect
        self.rect.clamp_ip(self.room.rect)

        # Testing slip through thin floors, hold down and press space for jump
        if self.floor == "2":
            if pressed[pygame.K_DOWN] and just_pressed[pygame.K_SPACE]:
                self.rect.y += 1

        # handle player hitting enemy type 1
        self.surf.fill("red")
        nearby_enemies = self.enemy_collision_layer.search(self.rect)
        if len(nearby_enemies):
            self.surf.fill("yellow")

        # handle player hitting door
        nearby_doors = self.door_collision_layer.search(self.rect)
        if len(nearby_doors):
            self.room.on_player_hit_door_change_room(
                nearby_doors[0].target_room_json_name, nearby_doors[0].name
            )

    def draw(self, screen: pygame.Surface, camera: pygame.FRect):
        screen.blit(self.surf, (self.rect.x - camera.x, self.rect.y - camera.y))
