import pygame

from const import HEIGHT, WIDTH
from definitions import PygameContext


def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    clock = pygame.time.Clock()

    return PygameContext(screen, clock)
