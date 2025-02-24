import pygame

# from room import Room
from const import TILE_SIZE


class Door:
    def __init__(self, x, y, target_room_json_name, name):
        # id for collision layer search, so others know what this is
        self.type = "door"
        self.surf: pygame.Surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.colr = "green"
        self.surf.fill(self.colr)  # Default color
        self.rect: pygame.FRect = self.surf.get_frect()
        # set pos is by rect bottom left
        self.rect.x = x
        self.rect.y = y

        self.target_room_json_name = target_room_json_name
        self.name = name

    def draw(self, screen: pygame.Surface, camera: pygame.FRect):
        screen.blit(self.surf, (self.rect.x - camera.x, self.rect.y - camera.y))
