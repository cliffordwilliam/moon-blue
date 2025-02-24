from dataclasses import dataclass

import pygame


@dataclass
class PygameContext:
    screen: pygame.Surface
    clock: pygame.time.Clock
