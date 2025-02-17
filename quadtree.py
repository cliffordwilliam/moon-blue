import pygame
import random
import time
from typing import List, Tuple, Optional

# Updated SomeObject class
class SomeObject:
    def __init__(self, rect: pygame.FRect, vel: Tuple[float, float], color: Tuple[int, int, int]) -> None:
        self.rect = rect  # rect holds both position and size
        self.vel = pygame.Vector2(vel)  # Velocity remains a Vector2
        self.color = color

    def move(self, bounds: pygame.FRect):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y

        # Bounce back if hitting the boundary
        if self.rect.left < bounds.left or self.rect.right > bounds.right:
            self.vel.x *= -1
        if self.rect.top < bounds.top or self.rect.bottom > bounds.bottom:
            self.vel.y *= -1

CACHE: dict[SomeObject, "QuadTree"] = {}
NATIVE_SIZE = (320, 180)
BIGGEST_ROOM = (320 * 2, 180 * 2)
NO_OF_ITEMS = 12000

class QuadTree:
    MAX_DEPTH: int = 8

    def __init__(self, rect: pygame.FRect, depth: int = 0) -> None:
        self.depth: int = depth
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
        self.items: List[SomeObject] = []
        self.children_quads: Optional[List[Optional[QuadTree]]] = [None] * 4

    def insert(self, item: SomeObject) -> None:
        for i, child in enumerate(self.children):
            if child.contains(item.rect):
                if self.depth + 1 < self.MAX_DEPTH:
                    if not self.children_quads[i]:
                        self.children_quads[i] = QuadTree(self.children[i], self.depth + 1)
                    self.children_quads[i].insert(item)
                    return

        self.items.append(item)
        CACHE[id(item)] = self

    def search(self, area: pygame.FRect) -> List[SomeObject]:
        items_in_area: List[SomeObject] = []
        self._search(area, items_in_area)
        return items_in_area

    def _search(self, area: pygame.FRect, items_in_area: List[SomeObject]) -> None:
        for item in self.items:
            if area.colliderect(item.rect):
                items_in_area.append(item)

        for i, child_quad in enumerate(self.children_quads):
            if child_quad:
                if area.contains(self.children[i]):
                    child_quad._get_all_items(items_in_area)
                elif self.children[i].colliderect(area):
                    child_quad._search(area, items_in_area)

    def _get_all_items(self, items_in_area: List[SomeObject]) -> None:
        for item in self.items:
            items_in_area.append(item)

        for child_quad in self.children_quads:
            if child_quad:
                child_quad._get_all_items(items_in_area)

    def remove(self, item: SomeObject) -> bool:
        item_id = id(item)
        if item_id in CACHE:
            quadtree = CACHE[item_id]
            if item in quadtree.items:
                quadtree.items.remove(item)
            del CACHE[item_id]  # Remove from CACHE
            return True
        return False

    def relocate(self, item: SomeObject) -> None:
        if self.remove(item):
            self.insert(item)

# Main example demo game class
class Example_StaticQuadTree:
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(NATIVE_SIZE)
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.is_using_quad: bool = True

        self.world_rect: pygame.FRect = pygame.FRect((0, 0), BIGGEST_ROOM)
        self.static_quad_tree: QuadTree = QuadTree(self.world_rect)
        self.objects: List[SomeObject] = []

        self.rand_float: callable = lambda a, b: random.uniform(a, b)

        self.create_objects()

        self.cam: pygame.FRect = pygame.FRect((0, 0), NATIVE_SIZE)  # Use pygame.FRect for the camera

    def create_objects(self) -> None:
        for _ in range(NO_OF_ITEMS):
            rect: pygame.FRect = pygame.FRect(
                self.rand_float(0, BIGGEST_ROOM[0]),
                self.rand_float(0, BIGGEST_ROOM[1]),
                self.rand_float(5, 20),
                self.rand_float(5, 20)
            )
            vel = (self.rand_float(-1, 1), self.rand_float(-1, 1))
            obj: SomeObject = SomeObject(rect, vel, (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ))
            self.static_quad_tree.insert(obj)
            self.objects.append(obj)

    def run(self) -> None:
        running: bool = True
        while running:
            self.screen.fill((0, 0, 0))
            start_time: float = time.time()
            object_count: int = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    items_in_screen = self.static_quad_tree.search(self.cam)
                    for obj in items_in_screen:
                        self.static_quad_tree.remove(obj)
                        self.objects.remove(obj)

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

            for obj in self.objects:
                obj.move(self.world_rect)
                self.static_quad_tree.relocate(obj)

            if pygame.key.get_just_pressed()[pygame.K_0]:
                self.is_using_quad = not self.is_using_quad

            if self.is_using_quad:
                # QUAD TREE MODE
                items_in_screen: List[SomeObject] = self.static_quad_tree.search(self.cam)
                for obj in items_in_screen:
                    pygame.draw.rect(self.screen, obj.color, pygame.FRect(obj.rect.x - self.cam.x, obj.rect.y - self.cam.y, obj.rect.w, obj.rect.h))
                    object_count += 1
            else:
                # LINEAR SEARCH MODE
                for obj in self.objects:
                    if self.cam.colliderect(pygame.FRect(obj.rect.x, obj.rect.y, obj.rect.w, obj.rect.h)):
                        pygame.draw.rect(self.screen, obj.color, pygame.FRect(obj.rect.x - self.cam.x, obj.rect.y - self.cam.y, obj.rect.w, obj.rect.h))
                        object_count += 1

            elapsed_time: float = time.time() - start_time
            pygame.display.set_caption(f'{"Quad" if self.is_using_quad else "Linear"} {elapsed_time:.2f}s')

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    demo = Example_StaticQuadTree()
    demo.run()
