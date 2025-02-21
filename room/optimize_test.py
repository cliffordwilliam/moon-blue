# q - toggle quad on or off

import pygame
import raycast_utils
import tilemap_utils
import quadtree_utils
import random

# Constants
PARTICLE_COUNT = 200  # Number of particles

# Initialize Pygame
pygame.init()

# Set window dimensions
WIDTH, HEIGHT = 320, 180

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("Pygame Window")

# Load background image just so that its clear that i am moving around
background = pygame.image.load("room/map.png")

# Use tilemap json and png to make WORLD MAP and PRE RENDER BG and set room cam limit
data = tilemap_utils.tilemap_routine("test_2.json", "forest_of_illusion_tile_sheet.png")
width = data["width"]
height = data["height"]
tileheight = data["tileheight"]
world_map_grid_data = data["world_map_grid_data"]
pre_rendered_bg = data["pre_rendered_bg"]
room_limit_rect = pygame.FRect(0, 0, width * 16, height * 16)

class Player:
    def __init__(self, x, y):
        self.surf: pygame.Surface = pygame.Surface((7, 18))
        self.surf.fill("red")
        self.rect: pygame.FRect = self.surf.get_frect()
        self.rect.x = x
        self.rect.y = y

        self.max_run: float = 0.09  # Px / ms
        self.velocity: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
        self.decay: float = 0.01

    def update(self, keys, dt):
        # Get dir
        direction_horizontal = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        direction_vertical = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        # Update vel with dir
        self.velocity.x = raycast_utils.exp_decay(self.velocity.x, direction_horizontal * self.max_run, self.decay, dt)
        self.velocity.y = raycast_utils.exp_decay(self.velocity.y, direction_vertical * self.max_run, self.decay, dt)
        # Move and slide just like in Godot
        contact_normal = pygame.Vector2(0.0, 0.0)
        contact_point = pygame.Vector2(0.0, 0.0)
        raycast_utils.resolve_vel_against_solid_tiles(self.rect, dt, self.velocity, tileheight, width, height, world_map_grid_data, contact_point, contact_normal)
        # Update pos
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        # Clamp in screen rect
        self.rect.clamp_ip(room_limit_rect)

    def draw(self, screen: pygame.Surface, camera: pygame.FRect):
        screen.blit(self.surf, (self.rect.x - camera.x, self.rect.y - camera.y))


class Particle:
    def __init__(self, x, y):
        self.surf: pygame.Surface = pygame.Surface((7, 18))
        self.colr = "blue"
        self.surf.fill(self.colr)  # Default color
        self.rect: pygame.FRect = self.surf.get_frect()
        self.rect.x = x
        self.rect.y = y

        self.max_run: float = 0.03  # Px / ms
        self.velocity: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
        self.decay: float = 0.01

        self.direction_horizontal = 1
        self.direction_vertical = 1

        self.bounce_cooldown = 0  # Cooldown timer in ms

    def update(self, dt):
        # Reduce cooldown timer
        if self.bounce_cooldown > 0:
            self.bounce_cooldown -= dt
        # Update vel with dir
        self.velocity.x = raycast_utils.exp_decay(self.velocity.x, self.direction_horizontal * self.max_run, self.decay, dt)
        self.velocity.y = raycast_utils.exp_decay(self.velocity.y, self.direction_vertical * self.max_run, self.decay, dt)
        # Move and slide just like in Godot
        contact_normal = pygame.Vector2(0.0, 0.0)
        contact_point = pygame.Vector2(0.0, 0.0)
        raycast_utils.resolve_vel_against_solid_tiles(self.rect, dt, self.velocity, tileheight, width, height, world_map_grid_data, contact_point, contact_normal)
        self.direction_horizontal = contact_normal.x or self.direction_horizontal
        self.direction_vertical = contact_normal.y or self.direction_vertical
        # Update pos
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        # Clamp in screen rect
        self.rect.clamp_ip(room_limit_rect)

    def bounce_with(self, other):
        """Handles bouncing between two particles"""
        # Reset color to default before checking collisions
        if self.bounce_cooldown <= 0 and other.bounce_cooldown <= 0:
            self.surf.fill("green")
            # Randomize new directions ensuring they are different
            new_dirs = [-1, 1]
            random.shuffle(new_dirs)  # Shuffle to make them unique

            self.direction_horizontal = new_dirs[0]
            other.direction_horizontal = new_dirs[1]

            random.shuffle(new_dirs)  # Shuffle again for vertical movement
            self.direction_vertical = new_dirs[0]
            other.direction_vertical = new_dirs[1]

            # Set cooldown to prevent instant rebouncing
            self.bounce_cooldown = 300  # 200ms cooldown
            other.bounce_cooldown = 300

    def draw(self, screen: pygame.Surface, camera: pygame.FRect):
        screen.blit(self.surf, (self.rect.x - camera.x, self.rect.y - camera.y))

player = Player(16, 16)
particles = [Particle(random.randint(64, width * 16 - 64), random.randint(64, height * 16 - 64)) for _ in range(PARTICLE_COUNT)]
quad = quadtree_utils.QuadTree(pygame.FRect(0, 0, width * 16, height * 16))

# Camera viewport
camera = pygame.FRect(0, 0, WIDTH, HEIGHT)
use_quadtree = True

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60)  # Cap at 60 FPS
    pygame.display.set_caption(f"Iteration Time: {dt} ms | Quadtree: {'ON' if use_quadtree else 'OFF'}")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            use_quadtree = not use_quadtree
    
    # Get key states
    keys = pygame.key.get_pressed()
    player.update(keys, dt)
    quad.clear()
    for particle in particles:
        particle.surf.fill(particle.colr)
        quad.insert(particle)  # you want to put the numerous things that others wanna look for
        # iter per particle to find other particle
        nearby = quad.search(particle.rect) if use_quadtree else [p for p in particles if p.rect.colliderect(particle.rect) and p != particle]
        for other in nearby:
            if other != particle:
                particle.bounce_with(other)
    
    # use player rect to find nearby particles
    player.surf.fill("red")
    nearby = quad.search(player.rect) if use_quadtree else [p for p in particles if p.rect.colliderect(player.rect)]
    if len(nearby):
        player.surf.fill("yellow")

    camera.center = player.rect.center
    camera.clamp_ip(room_limit_rect)
    
    screen.fill("black")
    screen.blit(background, (-camera.x, -camera.y))
    screen.blit(pre_rendered_bg, (-camera.x, -camera.y))
    player.draw(screen, camera)

    # use cam rect to find nearby particle to draw and update them
    nearby = quad.search(camera) if use_quadtree else particles
    for particle in nearby:
        particle.update(dt)
        particle.draw(screen, camera)
    pygame.display.update()
pygame.quit()
