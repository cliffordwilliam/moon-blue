import pygame
import raycast_utils
import tilemap_utils
import random

# Constants
PARTICLE_COUNT = 1000  # Number of particles

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
        self.default_color = "blue"
        self.collision_color = "yellow"
        self.surf.fill(self.default_color)  # Default color
        self.rect: pygame.FRect = self.surf.get_frect()
        self.rect.x = x
        self.rect.y = y

        self.max_run: float = 0.09  # Px / ms
        self.velocity: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
        self.decay: float = 0.01

        self.direction_horizontal = 1
        self.direction_vertical = 1

    def update(self, dt, player_rect):
        # Check for collision with player
        if self.rect.colliderect(player_rect):
            self.surf.fill(self.collision_color)
        else:
            self.surf.fill(self.default_color)
        
        # Update vel with dir
        self.velocity.x = raycast_utils.exp_decay(self.velocity.x, self.direction_horizontal * self.max_run, self.decay, dt)
        self.velocity.y = raycast_utils.exp_decay(self.velocity.y, self.direction_vertical * self.max_run, self.decay, dt)
        # Move and slide just like in Godot
        contact_normal = pygame.Vector2(0.0, 0.0)
        contact_point = pygame.Vector2(0.0, 0.0)
        raycast_utils.resolve_vel_against_solid_tiles(self.rect, dt, self.velocity, tileheight, width, height, world_map_grid_data, contact_point, contact_normal)
        self.direction_horizontal = contact_normal.x if contact_normal.x != 0 else self.direction_horizontal
        self.direction_vertical = contact_normal.y if contact_normal.y != 0 else self.direction_vertical
        # Update pos
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        # Clamp in screen rect
        self.rect.clamp_ip(room_limit_rect)

    def draw(self, screen: pygame.Surface, camera: pygame.FRect):
        screen.blit(self.surf, (self.rect.x - camera.x, self.rect.y - camera.y))

player = Player(16, 16)
particles = [Particle(random.randint(64, width * 16 - 64), random.randint(64, height * 16 - 64)) for _ in range(PARTICLE_COUNT)]

# Camera viewport
camera = pygame.FRect(0, 0, WIDTH, HEIGHT)

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60)  # Cap at 60 FPS
    pygame.display.set_caption(f"Iteration Time: {dt} ms")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Get key states
    keys = pygame.key.get_pressed()
    player.update(keys, dt)
    for particle in particles:
        particle.update(dt, player.rect)
    
    # Update camera offset based on player position
    camera.center = player.rect.center
    camera.clamp_ip(room_limit_rect)
    
    # Blit the background image with offset
    screen.fill("black")
    screen.blit(background, (-camera.x, -camera.y))
    screen.blit(pre_rendered_bg, (-camera.x, -camera.y))  # Draw the pre-rendered grid world map

    # Draw player with camera offset
    player.draw(screen, camera)
    for particle in particles:
        particle.draw(screen, camera)
    
    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
