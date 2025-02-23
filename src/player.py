import pygame

# from room import Room
from utils import raycast_utils


class Player:
    def __init__(self, x, y, room):
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

    def update(self, keys, dt):
        # Get dir
        direction_horizontal = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        direction_vertical = keys[pygame.K_DOWN] - keys[pygame.K_UP]
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
        raycast_utils.resolve_vel_against_solid_tiles(
            self.rect,
            dt,
            self.velocity,
            self.room.tileheight,
            self.room.width,
            self.room.height,
            self.room.room_map_grid_data_solid,
            contact_point,
            contact_normal,
        )
        # Update pos
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        # Clamp in screen rect
        self.rect.clamp_ip(self.room.rect)

    def draw(self, screen: pygame.Surface, camera: pygame.FRect):
        screen.blit(self.surf, (self.rect.x - camera.x, self.rect.y - camera.y))
