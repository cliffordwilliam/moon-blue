import pygame
import random
import time
from typing import List, Tuple, Optional


# Updated SomeObjectWithArea class
class SomeObjectWithArea:
    def __init__(self, rect: pygame.FRect, vVel: Tuple[float, float], color: Tuple[int, int, int]) -> None:
        self.rect: pygame.FRect = rect  # rect holds both position and size
        self.vVel: pygame.Vector2 = pygame.Vector2(vVel)  # Velocity remains a Vector2
        self.color: Tuple[int, int, int] = color

class StaticQuadTree:
    MAX_DEPTH: int = 8

    def __init__(self, rect: pygame.FRect, nDepth: int = 0) -> None:
        self.depth: int = nDepth
        self.resize(rect)

    def resize(self, rect: pygame.FRect) -> None:
        self.clear()
        self.rect: pygame.FRect = rect
        half_width: float = self.rect.w / 2
        half_height: float = self.rect.h / 2
        self.children: List[pygame.FRect] = [
            pygame.FRect(self.rect.x, self.rect.y, half_width, half_height),  # Top Left
            pygame.FRect(self.rect.x + half_width, self.rect.y, half_width, half_height),  # Top Right
            pygame.FRect(self.rect.x, self.rect.y + half_height, half_width, half_height),  # Bottom Left
            pygame.FRect(self.rect.x + half_width, self.rect.y + half_height, half_width, half_height)  # Bottom Right
        ]

    def clear(self) -> None:
        self.items: List[Tuple[pygame.FRect, SomeObjectWithArea]] = []
        self.children_quads: Optional[List[Optional[StaticQuadTree]]] = [None] * 4

    def insert(self, item: SomeObjectWithArea, item_rect: pygame.FRect) -> None:
        for i, child in enumerate(self.children):
            if child.collidepoint(item_rect.x, item_rect.y):
                if self.depth + 1 < self.MAX_DEPTH:
                    if not self.children_quads[i]:
                        self.children_quads[i] = StaticQuadTree(self.children[i], self.depth + 1)
                    self.children_quads[i].insert(item, item_rect)
                    return

        self.items.append((item_rect, item))

    def search(self, area: pygame.FRect) -> List[SomeObjectWithArea]:
        items_in_area: List[SomeObjectWithArea] = []
        self._search(area, items_in_area)
        return items_in_area

    def _search(self, area: pygame.FRect, items_in_area: List[SomeObjectWithArea]) -> None:
        for item_rect, item in self.items:
            if area.colliderect(item_rect):
                items_in_area.append(item)

        for i, child_quad in enumerate(self.children_quads):
            if child_quad:
                if area.contains(self.children[i]):
                    child_quad._get_all_items(items_in_area)
                elif self.children[i].colliderect(area):
                    child_quad._search(area, items_in_area)

    def _get_all_items(self, items_in_area: List[SomeObjectWithArea]) -> None:
        for item_rect, item in self.items:
            items_in_area.append(item)

        for child_quad in self.children_quads:
            if child_quad:
                child_quad._get_all_items(items_in_area)

# Main example demo game class
class Example_StaticQuadTree:
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((320, 180))
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.fWidth: float = 640.0
        self.fHeight: float = 360.0
        self.bUseQuadTree: bool = True

        self.world_rect: pygame.FRect = pygame.FRect(0, 0, self.fWidth, self.fHeight)
        self.treeObjects: StaticQuadTree = StaticQuadTree(self.world_rect)
        self.vecObjects: List[SomeObjectWithArea] = []

        self.rand_float: callable = lambda a, b: random.uniform(a, b)

        self.create_objects()

        self.cam: pygame.FRect = pygame.FRect(0, 0, 320, 180)  # Use pygame.FRect for the camera

    def create_objects(self) -> None:
        for _ in range(10000):
            # Creating objects with pygame.FRect for position and size
            rect: pygame.FRect = pygame.FRect(self.rand_float(0, self.fWidth), self.rand_float(0, self.fHeight),
                                              self.rand_float(0.1, 100), self.rand_float(0.1, 100))
            obj: SomeObjectWithArea = SomeObjectWithArea(rect, (0, 0), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            # Insert the object with the rect for position and size
            self.treeObjects.insert(obj, obj.rect)
            self.vecObjects.append(obj)

    def run(self) -> None:
        running: bool = True
        while running:
            self.screen.fill((0, 0, 0))
            start_time: float = time.time()
            nObjectCount: int = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Pan the camera with arrow keys
            keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.cam.y -= 10
            if keys[pygame.K_DOWN]:
                self.cam.y += 10
            if keys[pygame.K_LEFT]:
                self.cam.x -= 10
            if keys[pygame.K_RIGHT]:
                self.cam.x += 10

            # Clamp the camera within the game world
            self.cam.clamp_ip(self.world_rect)

            if pygame.key.get_just_pressed()[pygame.K_0]:
                self.bUseQuadTree = not self.bUseQuadTree

            if self.bUseQuadTree:
                # QUAD TREE MODE
                items_in_screen: List[SomeObjectWithArea] = self.treeObjects.search(self.cam)
                for obj in items_in_screen:
                    pygame.draw.rect(self.screen, obj.color, pygame.FRect(obj.rect.x - self.cam.x, obj.rect.y - self.cam.y, obj.rect.w, obj.rect.h))
                    nObjectCount += 1
            else:
                # LINEAR SEARCH MODE
                for obj in self.vecObjects:
                    if self.cam.colliderect(pygame.FRect(obj.rect.x, obj.rect.y, obj.rect.w, obj.rect.h)):
                        pygame.draw.rect(self.screen, obj.color, pygame.FRect(obj.rect.x - self.cam.x, obj.rect.y - self.cam.y, obj.rect.w, obj.rect.h))
                        nObjectCount += 1

            elapsed_time: float = time.time() - start_time
            pygame.display.set_caption(f'{"Quad" if self.bUseQuadTree else "Linear"} {elapsed_time:.4f}s')

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    demo = Example_StaticQuadTree()
    demo.run()
