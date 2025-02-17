"""
This bit explains the use of quadtree with a small demo

Run this to see how it works with Python 3.13.2 + pygame-ce 2.5.3
"""

import pygame
from typing import Optional
import random  # for demo

class Actor:
    """
    What is this?
    This represent game actors in a room

    Update the shape however you need it to be later

    This is the minimal example, that they MUST have rect and id!
    """
    def __init__(self, actor_id: int, rect: pygame.FRect):
        self.id = actor_id
        self.rect = rect
        self.vx = random.uniform(-2, 2)  # Random velocity X
        self.vy = random.uniform(-2, 2)  # Random velocity Y

    def move(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Bounce off edges
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.vx *= -1
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vy *= -1

# Cache connections between actors and their quad room
actor_id_to_quad_instance_cache: dict[int, "Quadtree"] = {}

# Const
MAX_QUADTREE_SUB_DIVISION_DEPTH = 8
QUADTREE_NUMBER_OF_KIDS = 4

class Quadtree:
    """
    What is this?
    You want to use this to check if 1 rect collides with another rect in a finite room, given that there are many rects

    For example
    You have a room filled with many walking npc, the player is running around and the camera follows player
    You want to see which npc collides with camera so you can activate them, else you deactivate the rest

    npcs_list_in_camera = quadtree.search(camera.rect)
    Then iterate and call each of the npc draw and update

    When you first instance npc, add them to quadtree with its insert method

    If you want to delete something you find? For example
    You have a moving bullet in a room filled with enemies
    If you find something that overlap with bullet you want to delete them?
    Use the remove actor method

    How to handle when npc are moving around?
    You want to move the npc first, and then you call the quadtree relocate and pass the moved actor inside
    """
    def __init__(self, rect: pygame.FRect, depth: int):
        # My rect
        self.rect: pygame.FRect = rect

        # My actors
        self.actors: list[Actor] = []

        # Keeps track of my depth level, if I'm at max depth I won't make more kids
        self.depth: int = depth

        # Container to hold my quad kids
        self.kids: list[Optional[Quadtree]] = [None] * QUADTREE_NUMBER_OF_KIDS

        # I have prepared my quad kids rect for making them later
        child_width: float = self.rect.width / 2.0
        child_height: float = self.rect.height / 2.0
        self.kids_rects: list[pygame.FRect] = [
            pygame.FRect(
                (
                    self.rect.x,
                    self.rect.y,
                ),
                (
                    child_width,
                    child_height,
                ),
            ),
            pygame.FRect(
                (
                    self.rect.x + child_width,
                    self.rect.y,
                ),
                (
                    child_width,
                    child_height,
                ),
            ),
            pygame.FRect(
                (
                    self.rect.x,
                    self.rect.y + child_height,
                ),
                (
                    child_width,
                    child_height,
                ),
            ),
            pygame.FRect(
                (
                    self.rect.x + child_width,
                    self.rect.y + child_height,
                ),
                (
                    child_width,
                    child_height,
                ),
            ),
        ]

    def insert(self, given_actor: Actor) -> None:
        # Iter my kids
        for i in range(QUADTREE_NUMBER_OF_KIDS):
            kid_rect = self.kids_rects[i]
            kid = self.kids[i]
            # Inserted actor falls completely inside one of my kids (not landing and touching kids edges)
            if kid_rect.contains(given_actor.rect):
                # Check if I'm not at max depth guard
                if self.depth + 1 < MAX_QUADTREE_SUB_DIVISION_DEPTH:
                    # Check if kid is not instanced yet? Make new kid and tell it that its at a lower level + 1
                    if not kid:
                        kid = Quadtree(kid_rect, self.depth + 1)
                        self.kids[i] = kid
                    # Give the inserted actor into that kid
                    kid.insert(given_actor)
                    return

        # If none of the condition above is true then this actor is mine!
        self.actors.append(given_actor)

        # Update cache, bind this inserted actor and myself as instance
        actor_id_to_quad_instance_cache[given_actor.id] = self

    def search(self, search_rect: pygame.FRect) -> list:
        # Prepare the found container
        found_actors: list[Actor] = []
        
        # The quadtree magic that gets you fast collision check!
        self._search_helper(search_rect, found_actors)

        # Returns all found actors!
        return found_actors

    def relocate(self, given_actor: Actor) -> None:
        # Relocate is just remove and re insert
        if self._remove_actor(given_actor):
            self.insert(given_actor)

    def _search_helper(self, search_rect: pygame.FRect, found_actors: list[Actor]) -> None:
        # Iter all actors in me
        for actor in self.actors:
            # If the passed in search rect hits one of my actors? Collect them to found container
            if search_rect.colliderect(actor.rect):
                found_actors.append(actor)

        # Iter my kids
        for i in range(QUADTREE_NUMBER_OF_KIDS):
            kid_rect = self.kids_rects[i]
            kid = self.kids[i]
            if kid:
                # If the given search rect completely engulf this kid? Then batch dump ALL of this kid and its sub kids actors to found container
                if search_rect.contains(kid_rect):
                    kid._add_actors(found_actors)
                # If given search rect hits this kid? Tell it to use search rect to see if some of its owned actors are in it 
                elif kid_rect.colliderect(search_rect):
                    kid._search_helper(search_rect, found_actors)

    def _add_actors(self, found_actors: list[Actor]) -> None:
        # Dump all of my actors in found container
        for actor in self.actors:
            found_actors.append(actor)

        # Tell my kids to do likewise
        for kid in self.kids:
            if kid:
                kid._add_actors(found_actors)

    def _remove_actor(self, to_be_deleted_actor: Actor) -> bool:
        # Delete quad first from cache (this uses pop so that if not found it wont throw)
        quadtree = actor_id_to_quad_instance_cache.pop(to_be_deleted_actor.id, None)
        # If actor in cache and in quad, delete it
        if quadtree and to_be_deleted_actor in quadtree.actors:
            quadtree.actors.remove(to_be_deleted_actor)
            return True
        return False
    
# Small demo -------------------------------------------------------------------------------------

WIDTH, HEIGHT = 800, 600
ACTOR_SIZE = 10
NUM_ACTORS = 5000
SEARCH_SIZE = 50
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

quadtree = Quadtree(pygame.FRect(0, 0, WIDTH, HEIGHT), 0)
actors = []

for i in range(NUM_ACTORS):
    x, y = random.randint(0, WIDTH - ACTOR_SIZE), random.randint(0, HEIGHT - ACTOR_SIZE)
    rect = pygame.FRect(x, y, ACTOR_SIZE, ACTOR_SIZE)
    actor = Actor(i, rect)
    actors.append(actor)
    quadtree.insert(actor)

search_rect = pygame.FRect(0, 0, SEARCH_SIZE, SEARCH_SIZE)

running = True
while running:
    screen.fill(WHITE)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    search_rect.topleft = (mouse_x - SEARCH_SIZE // 2, mouse_y - SEARCH_SIZE // 2)
    
    quadtree = Quadtree(pygame.FRect(0, 0, WIDTH, HEIGHT), 0)  # Rebuild Quadtree
    for actor in actors:
        actor.move()
        quadtree.insert(actor)
    
    found_actors = quadtree.search(search_rect)
    found_ids = {actor.id for actor in found_actors}
    
    for actor in actors:
        color = RED if actor.id in found_ids else BLUE
        pygame.draw.rect(screen, color, actor.rect)
    
    pygame.draw.rect(screen, GREEN, search_rect, 2)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for actor in found_actors:
                if quadtree._remove_actor(actor):
                    actors.remove(actor)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
