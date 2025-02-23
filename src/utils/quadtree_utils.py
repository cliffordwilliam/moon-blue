# space - toggle quad or naive
# q - toggle draw quad
# p - toggle pause

import pygame
from typing import List


class QuadTree:
    MAX_DEPTH: int = 6
    MAX_ITEMS: int = 4

    def __init__(self, rect: pygame.FRect, depth: int = 0) -> None:
        self.rect: pygame.FRect = rect
        self.depth: int = depth
        self.items: List[any] = []
        self.children: List[QuadTree] = []

    def subdivide(self) -> None:
        if self.children:
            return
        half_w: float = self.rect.w / 2
        half_h: float = self.rect.h / 2
        for dx, dy in [(0, 0), (half_w, 0), (0, half_h), (half_w, half_h)]:
            self.children.append(
                QuadTree(
                    pygame.FRect(self.rect.x + dx, self.rect.y + dy, half_w, half_h),
                    self.depth + 1,
                )
            )

    def insert(self, particle: any) -> bool:
        if not self.rect.colliderect(particle.rect):
            return False
        if len(self.items) < self.MAX_ITEMS or self.depth >= self.MAX_DEPTH:
            self.items.append(particle)
            return True
        if not self.children:
            self.subdivide()
        for child in self.children:
            if child.insert(particle):
                return True
        return False

    def search(self, area: pygame.FRect) -> List[any]:
        found: List[any] = [p for p in self.items if area.colliderect(p.rect)]
        for child in self.children:
            if child.rect.colliderect(area):
                found.extend(child.search(area))
        return found

    def clear(self) -> None:
        self.items.clear()
        for child in self.children:
            child.clear()
        self.children = []
