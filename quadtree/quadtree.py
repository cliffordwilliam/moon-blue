# space - toggle quad or naive
# q - toggle draw quad
# p - toggle pause

import pygame
import random
import time
from typing import List, Tuple

# Constants
WIDTH: int = 640
HEIGHT: int = 360
PARTICLE_COUNT: int = 10
PARTICLE_RADIUS: int = 2
MAX_VEL: int = 1

# Initialize Pygame
pygame.init()
screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
clock: pygame.time.Clock = pygame.time.Clock()
use_quadtree: bool = True
draw_quad_tree: bool = False
paused: bool = False

def draw_quad(quad: "QuadTree", screen: pygame.Surface) -> None:
    pygame.draw.rect(screen, (0, 0, 255), quad.rect, 1)
    for child in quad.children:
        draw_quad(child, screen)

class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int]) -> None:
        self.rect: pygame.FRect = pygame.FRect(x, y, PARTICLE_RADIUS * 2, PARTICLE_RADIUS * 2)
        self.vel: pygame.Vector2 = pygame.Vector2(vx, vy)
        self.color: Tuple[int, int, int] = color

    def move(self, bounds: pygame.FRect) -> None:
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y

        # Bounce off walls
        if self.rect.left < bounds.left or self.rect.right > bounds.right:
            self.vel.x *= -1
        if self.rect.top < bounds.top or self.rect.bottom > bounds.bottom:
            self.vel.y *= -1

class QuadTree:
    MAX_DEPTH: int = 6
    MAX_ITEMS: int = 4

    def __init__(self, rect: pygame.FRect, depth: int = 0) -> None:
        self.rect: pygame.FRect = rect
        self.depth: int = depth
        self.items: List[Particle] = []
        self.children: List[QuadTree] = []

    def subdivide(self) -> None:
        if self.children:
            return
        half_w: float = self.rect.w / 2
        half_h: float = self.rect.h / 2
        for dx, dy in [(0, 0), (half_w, 0), (0, half_h), (half_w, half_h)]:
            self.children.append(QuadTree(pygame.FRect(self.rect.x + dx, self.rect.y + dy, half_w, half_h), self.depth + 1))

    def insert(self, particle: Particle) -> bool:
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

    def search(self, area: pygame.FRect) -> List[Particle]:
        found: List[Particle] = [p for p in self.items if area.colliderect(p.rect)]
        for child in self.children:
            if child.rect.colliderect(area):
                found.extend(child.search(area))
        return found

    def clear(self) -> None:
        self.items.clear()
        for child in self.children:
            child.clear()
        self.children = []

# Initialize particles and quadtree
particles: List[Particle] = [Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(-MAX_VEL, MAX_VEL), random.uniform(-MAX_VEL, MAX_VEL), (0, 255, 0)) for _ in range(PARTICLE_COUNT)]
quad: QuadTree = QuadTree(pygame.FRect(0, 0, WIDTH, HEIGHT))

running: bool = True
while running:
    start_time: float = time.time()
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                use_quadtree = not use_quadtree
            if event.key == pygame.K_q:
                draw_quad_tree = not draw_quad_tree
            if event.key == pygame.K_p:
                paused = not paused

    quad.clear()
    for particle in particles:
        quad.insert(particle)

    for particle in particles:
        if use_quadtree:
            nearby: List[Particle] = quad.search(particle.rect)
        else:
            nearby: List[Particle] = [p for p in particles if p.rect.colliderect(particle.rect) and p != particle]
        
        for other in nearby:
            if other != particle:
                particle.vel, other.vel = other.vel, particle.vel  # Simple bounce swap
        
        if not paused:
            particle.move(pygame.FRect(0, 0, WIDTH, HEIGHT))
        
        # Draw as rectangle instead of circle
        pygame.draw.rect(screen, particle.color, particle.rect)
    
    if use_quadtree and draw_quad_tree:
        draw_quad(quad, screen)
    
    elapsed_time: float = (time.time() - start_time) * 1000  # Convert to ms
    pygame.display.set_caption(f"{'Quadtree' if use_quadtree else 'Naive'} Mode - {'Paused' if paused else 'Running'} - Frame Time: {elapsed_time:.2f} ms")
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
