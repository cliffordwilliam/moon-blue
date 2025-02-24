import pygame
from math import exp

# note
# 1. camera finds candidate moving enemy rects in camera
# 2. player when shooting, will just make a line from its origin to mouse position
# 3. use the bottom func for ray vs rect, if it does hit something then player hits enemy, enemy can be another rect bullet or just enemy
# 4. make sure that player, enemy and enemy bullets are slow, but maybe also have enemy that can also shoot ray at you too
# 5. move slow so that there is no chance that you passes something through, slow as in in next frame you do not cover more than your half size

# For player to query collision (world map is just string, there are no boxes, this is the only solid box)
one_tile_rect = pygame.FRect(0, 0, 16, 16)


def determine_movement_direction(velocity_vector: pygame.Vector2) -> tuple[int, int]:
    x, y = velocity_vector.x, velocity_vector.y

    direction_x = 0 if abs(x) <= 0.01 else (1 if x > 0 else -1)
    direction_y = 0 if abs(y) <= 0.01 else (1 if y > 0 else -1)

    return direction_x, direction_y


def ray_vs_rect(
    ray_origin: pygame.Vector2,
    ray_dir: pygame.Vector2,
    target_rect: pygame.FRect,
    contact_point: pygame.Vector2,
    contact_normal: pygame.Vector2,
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
    contact_point = ray_origin + t_hit_near[0] * ray_dir

    # Compute contact normal
    if t_near.x > t_near.y:
        contact_normal.x, contact_normal.y = (1, 0) if ray_dir.x < 0 else (-1, 0)
    elif t_near.x < t_near.y:
        contact_normal.x, contact_normal.y = (0, 1) if ray_dir.y < 0 else (0, -1)
    else:
        if one_over_ray_dir_x < 0 and one_over_ray_dir_y < 0:
            contact_normal.x, contact_normal.y = (1, 1)
        elif one_over_ray_dir_x > 0 and one_over_ray_dir_y > 0:
            contact_normal.x, contact_normal.y = (-1, -1)
        elif one_over_ray_dir_x < 0 and one_over_ray_dir_y > 0:
            contact_normal.x, contact_normal.y = (1, -1)
        elif one_over_ray_dir_x > 0 and one_over_ray_dir_y < 0:
            contact_normal.x, contact_normal.y = (-1, 1)

    return True


def dynamic_rect_vs_rect(
    input_velocity: pygame.Vector2,
    collider_rect: pygame.FRect,
    target_rect: pygame.FRect,
    contact_point: pygame.Vector2,
    contact_normal: pygame.Vector2,
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


def get_tile_and_position(
    world_tu_x: int,
    world_tu_y: int,
    width: int,
    height: int,
    world_map_grid_data: list[str],
    tileheight: int,
) -> tuple[str, tuple[int, int]]:
    """
    Returns the tile type and its pixel position (x, y).
    Returns ("-1", (-1, -1)) if out of bounds.
    """
    if 0 <= world_tu_x < width and 0 <= world_tu_y < height:
        tile = world_map_grid_data[world_tu_y * width + world_tu_x]
        return tile, (world_tu_x * tileheight, world_tu_y * tileheight)
    else:
        return "-1", (-1, -1)  # Out of bounds


def compute_range(start: int, length: int, direction: int) -> range:
    if direction == 1:  # Moving forward or no movement
        return range(start, start + length)
    elif direction == -1:  # Moving backward
        return range(start + length - 1, start - 1, -1)
    else:  # No movement
        return range(start, start + length)


def resolve_vel_against_solid_tiles(
    given_rect: pygame.FRect,
    dt: int,
    velocity: pygame.Vector2,
    tileheight: pygame.FRect,
    width: int,
    height: int,
    world_map_grid_data: list[str],
    contact_point: pygame.Vector2,
    contact_normal: pygame.Vector2,
    is_player: bool = False,
):
    """
    Vel is immutable, just pass it in and after you r done calling this the val updates! This thing returns what you hit as well, tile type in str
    """

    tile_you_hit = ""

    # Compute the future position based on velocity and delta time
    distance_vector = velocity * dt
    future_rect = given_rect.move(distance_vector.x, distance_vector.y)

    # Get the bounds of the combined rect
    combined_rect = given_rect.union(future_rect)

    # Truncate the bounds to tile coordinates
    l_tu, t_tu = (
        int(combined_rect.left // tileheight),
        int(combined_rect.top // tileheight),
    )
    r_tu, b_tu = (
        int(combined_rect.right // tileheight),
        int(combined_rect.bottom // tileheight),
    )

    # Collect solid tiles in the combined rect
    combined_rect_width_ru = r_tu - l_tu + 1
    combined_rect_height_ru = b_tu - t_tu + 1
    combined_rect_x_ru = l_tu
    combined_rect_y_ru = t_tu

    # Get direction
    direction_x, direction_y = determine_movement_direction(velocity)

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
                width,
                height,
                world_map_grid_data,
                tileheight,
            )
            # Ignore air or out of bound
            if tile == "0" or tile == "-1":
                continue

            # update what u hit
            tile_you_hit = tile

            # Prepare query tile pos
            one_tile_rect.x = position[0]
            one_tile_rect.y = position[1]
            t_hit_near = [0.0]
            # This one is passed the correct sorted, so returns correct data like t hit near
            hit = dynamic_rect_vs_rect(
                velocity,
                given_rect,
                one_tile_rect,
                contact_point,
                contact_normal,
                t_hit_near,
                dt,
            )
            if hit:
                # PLAYER ONLY do not resolve vel if moving upward and hitting thin
                if is_player and tile_you_hit == "2" and contact_normal.y == 1:
                    return tile_you_hit

                # RESOLVE VEL
                velocity.x += contact_normal.x * abs(velocity.x) * (1 - t_hit_near[0])
                velocity.y += contact_normal.y * abs(velocity.y) * (1 - t_hit_near[0])

    return tile_you_hit


def exp_decay(a: float, b: float, decay: float, dt: int) -> float:
    return b + (a - b) * exp(-decay * dt)
