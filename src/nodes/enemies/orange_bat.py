import random
import pygame

# from room import Room
from nodes.animator import Animator
from utils import raycast_utils


class OrangeBat:
    def __init__(self, x, y, room, png, json, enemy_collision_layer):
        # id for collision layer search, so others know what this is
        self.type = "enemy"
        # enemy type 1 needs room ref, for move and slide and pos clamping within room limit
        self.room = room
        self.surf: pygame.Surface = png
        self.rect: pygame.FRect = pygame.FRect(0, 0, 8, 8)
        # set pos is by rect bottom left
        self.rect.x = x
        self.rect.y = y - self.rect.h

        self.max_run: float = 0.09  # Px / ms
        self.velocity: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
        self.decay: float = 0.01

        self.direction_horizontal = random.choice([1, -1])
        self.direction_vertical = random.choice([1, -1])

        self.bounce_cooldown = 0  # Cooldown timer in ms

        self.enemy_collision_layer = enemy_collision_layer

        # Initialize the animator
        self.animator = Animator(png, json)

    def update(self, dt):
        # Reduce cooldown timer
        if self.bounce_cooldown > 0:
            self.bounce_cooldown -= dt
        # Update vel with dir
        self.velocity.x = raycast_utils.exp_decay(
            self.velocity.x, self.direction_horizontal * self.max_run, self.decay, dt
        )
        self.velocity.y = raycast_utils.exp_decay(
            self.velocity.y, self.direction_vertical * self.max_run, self.decay, dt
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
            self.room.collision_layer,
            contact_point,
            contact_normal,
        )
        self.direction_horizontal = contact_normal.x or self.direction_horizontal
        self.direction_vertical = contact_normal.y or self.direction_vertical
        # Update pos
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        # Clamp in screen rect
        self.rect.clamp_ip(self.room.rect)

        # handle me bouncing off of each other
        nearby = self.enemy_collision_layer.search(self.rect)
        for other in nearby:
            if other != self:
                if other.__class__.__name__ == self.__class__.__name__:
                    self.bounce_with(other)

        # Update animation
        self.animator.update(dt)

    def bounce_with(self, other: "OrangeBat"):
        """Handles bouncing between my frens"""
        # Reset color to default before checking collisions
        if self.bounce_cooldown <= 0 and other.bounce_cooldown <= 0:
            # Randomize new directions ensuring they are different
            new_dirs = [-1, 1]
            random.shuffle(new_dirs)  # Shuffle to make them unique

            self.direction_horizontal = new_dirs[0]
            other.direction_horizontal = new_dirs[1]

            random.shuffle(new_dirs)  # Shuffle again for vertical movement
            self.direction_vertical = new_dirs[0]
            other.direction_vertical = new_dirs[1]

            # Set cooldown to prevent instant rebouncing
            self.bounce_cooldown = 400  # 200ms cooldown
            other.bounce_cooldown = 400

    def draw(self, screen: pygame.Surface, camera: pygame.FRect):
        frame_rect = self.animator.get_current_frame()
        screen.blit(
            self.surf, (self.rect.x - camera.x, self.rect.y - camera.y), frame_rect
        )
