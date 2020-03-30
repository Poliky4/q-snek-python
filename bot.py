import random

from snek import THING_SIZE, GAME_SIZE

up = (0, 1)
right = (1, 0)
down = (0, -1)
left = (-1, 0)

# MAX_RETRIES = 10
MAX_RETRIES = 100

def get_random_direction(snek, forbidden=[]):
    return random.choice([
        direction
        for direction
        in [up, right, down, left]
        if direction not in [
            snek.velocity#,
            # snek.inverse_velocity(snek.velocity)
        ] + forbidden
    ])

def play(state, tries=MAX_RETRIES):
    snek = state.snek
    apple = state.apple
    (sx, sy) = snek.position
    (ax, ay) = apple.position

    chosen_direction = None

    is_right = sx < ax
    is_left = sx > ax
    is_up = sy < ay
    is_down = sy > ay

    is_up_right = is_up and is_right
    is_up_left = is_up and is_left
    is_down_right = is_down and is_right
    is_down_left = is_down and is_left

    if is_up_right:
        chosen_direction = random.choice([up, right])
    elif is_up_left:
        chosen_direction = random.choice([up, left])
    elif is_down_right:
        chosen_direction = random.choice([down, right])
    elif is_down_left:
        chosen_direction = random.choice([down, left])
    elif is_right:
        chosen_direction = right
    elif is_left:
        chosen_direction = left
    elif is_up:
        chosen_direction = up
    elif is_down:
        chosen_direction = down

    if chosen_direction is None:
        chosen_direction = get_random_direction(snek)

    (vx, vy) = chosen_direction
    new_position = (
        sx + vx * THING_SIZE,
        sy + vy * THING_SIZE
    )

    is_outside = lambda position:(
        position[0] < 0 or
        position[1] < 0 or
        position[0] + snek.size > GAME_SIZE or
        position[1] + snek.size > GAME_SIZE
    )

    if (is_outside(new_position) or
    chosen_direction == snek.inverse_velocity(snek.velocity) or
    new_position in [thing.position for thing in snek.things]):
        if tries < 1:
            chosen_direction = get_random_direction(
                snek, forbidden=[chosen_direction])
        else:
            return play(state, tries=tries-1)

    snek.set_velocity(chosen_direction)

