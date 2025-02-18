import pygame
import sys
from math import exp

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 360
CELL_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 11
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = screen.get_rect()
pygame.display.set_caption("Move the Rectangle and Grid")

# Grid data representation
world_map_grid_data = (
    "00000000000000000000"
    "00000000000000000000"
    "00000000001000000000"
    "00000000010100000000"
    "00001011110100000000"
    "00001000000100000000"
    "00000000000100000000"
    "00000000000000000000"
    "00000000000000000000"
    "00000000000000000000"
    "00000000000000000000"
)

def determine_movement_direction(velocity_vector: pygame.Vector2) -> tuple[int, int]:
    x, y = velocity_vector.x, velocity_vector.y

    direction_x = 0 if abs(x) <= 0.01 else (1 if x > 0 else -1)
    direction_y = 0 if abs(y) <= 0.01 else (1 if y > 0 else -1)

    return direction_x, direction_y


def ray_vs_rect(
    ray_origin: pygame.Vector2,
    ray_dir: pygame.Vector2,
    target_rect: pygame.FRect,
    contact_point: list[pygame.Vector2],
    contact_normal: list[pygame.Vector2],
    t_hit_near: list,
) -> bool:
    """
    | True if light ray hits rect.
    |
    | Parameter needs ray origin, ray dir, target_rect.
    |
    | Need immutable list for extra info after computation.
    | contact_point, contact_normal, t_hit_near.
    """

    # Cache division
    one_over_ray_dir_x: float = 0.0
    one_over_ray_dir_y: float = 0.0
    sign: float = -1.0

    # Handle infinity
    if abs(ray_dir.x) < 0.1:
        if ray_dir.x > 0.0:
            sign = 1.0
        one_over_ray_dir_x = float("inf") * sign
    else:
        one_over_ray_dir_x = 1.0 / ray_dir.x

    # Handle infinity
    if abs(ray_dir.y) < 0.1:
        if ray_dir.y > 0.0:
            sign = 1.0
        one_over_ray_dir_y = float("inf") * sign
    else:
        one_over_ray_dir_y = 1.0 / ray_dir.y

    # Get near far time
    t_near = pygame.Vector2(
        (target_rect.x - ray_origin.x) * one_over_ray_dir_x,
        (target_rect.y - ray_origin.y) * one_over_ray_dir_y,
    )
    t_far = pygame.Vector2(
        (target_rect.x + target_rect.width - ray_origin.x) * one_over_ray_dir_x,
        (target_rect.y + target_rect.height - ray_origin.y) * one_over_ray_dir_y,
    )

    # Sort near far time
    if t_near.x > t_far.x:
        t_near.x, t_far.x = t_far.x, t_near.x
    if t_near.y > t_far.y:
        t_near.y, t_far.y = t_far.y, t_near.y

    # COLLISION RULE
    if t_near.x > t_far.y or t_near.y > t_far.x:
        return False

    # Get near far time
    t_hit_near[0] = max(t_near.x, t_near.y)
    t_hit_far: float = min(t_far.x, t_far.y)

    if t_hit_far < 0:
        return False

    # Compute contact point
    contact_point[0] = ray_origin + t_hit_near[0] * ray_dir

    # Compute contact normal
    if t_near.x > t_near.y:
        contact_normal[0].x, contact_normal[0].y = (1, 0) if ray_dir.x < 0 else (-1, 0)
    elif t_near.x < t_near.y:
        contact_normal[0].x, contact_normal[0].y = (0, 1) if ray_dir.y < 0 else (0, -1)

    return True


def dynamic_rect_vs_rect(
    input_velocity: pygame.Vector2,
    collider_rect: pygame.FRect,
    target_rect: pygame.FRect,
    contact_point: list[pygame.Vector2],
    contact_normal: list[pygame.Vector2],
    t_hit_near: list[float],
    dt: int,
) -> bool:
    """
    | If dynamic actor is not moving, returns False.
    """

    if not abs(input_velocity.x) > 0.0 and not abs(input_velocity.y) > 0.0:
        return False
    expanded_target: pygame.FRect = pygame.FRect(
        target_rect.x - collider_rect.width / 2,
        target_rect.y - collider_rect.height / 2,
        target_rect.width + collider_rect.width,
        target_rect.height + collider_rect.height,
    )
    hit = ray_vs_rect(
        pygame.Vector2(
            collider_rect.x + collider_rect.width / 2,
            collider_rect.y + collider_rect.height / 2,
        ),
        input_velocity * dt,
        expanded_target,
        contact_point,
        contact_normal,
        t_hit_near,
    )
    if hit:
        return t_hit_near[0] >= 0.0 and t_hit_near[0] < 1.0
    else:
        return False

# For player to query collision (world map is just string, there are no boxes, this is the only solid box)
one_tile_rect = pygame.FRect(0, 0, CELL_SIZE, CELL_SIZE)

def exp_decay(a: float, b: float, decay: float, dt: int) -> float:
    return b + (a - b) * exp(-decay * dt)

def get_tile_and_position(world_tu_x: int, world_tu_y: int) -> tuple[str, tuple[int, int]]:
    """
    Returns the tile type and its pixel position (x, y).
    Returns ("-1", (-1, -1)) if out of bounds.
    """
    if 0 <= world_tu_x < GRID_WIDTH and 0 <= world_tu_y < GRID_HEIGHT:
        tile = world_map_grid_data[world_tu_y * GRID_WIDTH + world_tu_x]
        return tile, (world_tu_x * CELL_SIZE, world_tu_y * CELL_SIZE)
    else:
        return "-1", (-1, -1)  # Out of bounds

def compute_range(start: int, length: int, direction: int) -> range:
    if direction == 1:  # Moving forward or no movement
        return range(start, start + length)
    elif direction == -1:  # Moving backward
        return range(start + length - 1, start - 1, -1)
    else:  # No movement
        return range(start, start + length)

class Player:
    def __init__(self, x, y):
        self.surf: pygame.Surface = pygame.Surface((32, 32))
        self.surf.fill("red")
        self.rect: pygame.FRect = self.surf.get_frect()

        self.max_run: float = 0.09  # Px / ms
        self.velocity: pygame.Vector2 = pygame.Vector2(0.0, 0.0)
        self.decay: float = 0.01

    def resolve_vel_against_solid_tiles(self, dt: int, velocity: pygame.Vector2) -> pygame.Vector2:
        """
        Return resolved velocity against solid tiles.
        """

        input_velocity: pygame.Vector2 = velocity
        resolved_velocity: pygame.Vector2 = velocity

        # Compute the future position based on velocity and delta time
        distance_vector = velocity * dt
        future_rect = self.rect.move(distance_vector.x, distance_vector.y)

        # Get the bounds of the combined rect
        combined_rect = self.rect.union(future_rect)

        # Truncate the bounds to tile coordinates
        l_tu, t_tu = int(combined_rect.left // CELL_SIZE), int(combined_rect.top // CELL_SIZE)
        r_tu, b_tu = int(combined_rect.right // CELL_SIZE), int(combined_rect.bottom // CELL_SIZE)

        # Collect solid tiles in the combined rect
        combined_rect_width_ru = r_tu - l_tu + 1
        combined_rect_height_ru = b_tu - t_tu + 1
        combined_rect_x_ru = l_tu
        combined_rect_y_ru = t_tu

        # Get direction
        direction_x, direction_y = determine_movement_direction(input_velocity)

        # Determine x and y iteration ranges based on the direction
        x_range = compute_range(combined_rect_x_ru, combined_rect_width_ru, direction_x)
        y_range = compute_range(combined_rect_y_ru, combined_rect_height_ru, direction_y)

        # Iterate region candidate
        for world_tu_x in x_range:
            for world_tu_y in y_range:
                # Get each one in solid_collision_map_list
                tile, position = get_tile_and_position(
                    world_tu_x,
                    world_tu_y,
                )
                # Ignore air or out of bound
                if tile == "0" or tile == "-1":
                    continue

                # Prepare query tile pos
                one_tile_rect.x = position[0]
                one_tile_rect.y = position[1]
                # Collision query with test rect
                contact_point = [pygame.Vector2(0, 0)]
                contact_normal = [pygame.Vector2(0, 0)]
                t_hit_near = [0.0]
                # This one is passed the correct sorted, so returns correct data like t hit near
                hit = dynamic_rect_vs_rect(
                    input_velocity,
                    self.rect,
                    one_tile_rect,
                    contact_point,
                    contact_normal,
                    t_hit_near,
                    dt,
                )
                if hit:
                    # RESOLVE VEL
                    resolved_velocity.x += contact_normal[0].x * abs(input_velocity.x) * (1 - t_hit_near[0])
                    resolved_velocity.y += contact_normal[0].y * abs(input_velocity.y) * (1 - t_hit_near[0])

        # Return the resolved vel
        return resolved_velocity

    def update(self, keys, dt):
        # Get dir
        direction_horizontal = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        direction_vertical = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        # Update vel with dir
        self.velocity.x = exp_decay(self.velocity.x, direction_horizontal * self.max_run, self.decay, dt)
        self.velocity.y = exp_decay(self.velocity.y, direction_vertical * self.max_run, self.decay, dt)
        # Move and slide just like in Godot
        self.velocity = self.resolve_vel_against_solid_tiles(dt, self.velocity)
        # Update pos
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        # Clamp in screen rect
        self.rect.clamp_ip(screen_rect)

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

# Pre-render the background grid surface
grid_surface = pygame.Surface((WIDTH, HEIGHT))
for row in range(GRID_HEIGHT):
    for col in range(GRID_WIDTH):
        cell_value = world_map_grid_data[row * GRID_WIDTH + col]
        color = WHITE if cell_value == '0' else BLACK
        pygame.draw.rect(
            grid_surface, color, pygame.FRect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )

def main():
    clock = pygame.time.Clock()
    player = Player(0, 0)
    running = True
    while running:
        dt = clock.tick(FPS)
        screen.fill(WHITE)  # Clear screen
        screen.blit(grid_surface, (0, 0))  # Draw the pre-rendered grid world map
        
        # Update then draw player
        keys = pygame.key.get_pressed()
        player.update(keys, dt)
        player.draw(screen)

        pygame.display.update()  # Update the screen
        
        # Query exit window btn
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()