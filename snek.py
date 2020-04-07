from enum import Enum
import math
import random

# GAME_SPEED = 7.5
# GAME_SPEED = 15
# GAME_SPEED = 30
GAME_SPEED = 60
FPS = 1 / GAME_SPEED

NBR_OF_CELLS = 20
SNEK_START_LENGTH = 3

class ACTIONS:
    UP = "UP"
    DOWN = "DOWN"
    RIGHT = "RIGHT"
    LEFT = "LEFT"

    up = (0, 1)
    right = (1, 0)
    down = (0, -1)
    left = (-1, 0)

class GameOverException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_all_positions():
    positions = []
    for y in range(NBR_OF_CELLS):
        for x in range(NBR_OF_CELLS):
            positions.append((x, y))
    return positions
all_positions = set(get_all_positions())
def get_new_apple_position(old_position, things):
    things_positions = [thing.position for thing in things]
    possible_positions = list(
        all_positions -
        set(things_positions) -
        set([old_position])
    )
    return random.choice(possible_positions)

class Thing:
    def __init__(self, x, y):
        self.position = (x, y)
        self.x = x
        self.y = y

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.position = (x, y)

class Snek(Thing):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocity = (1, 0)
        self.inputs = []
        self.things = []
        self.score = 0

        self.add_things(SNEK_START_LENGTH)

    def add_things(self, amount):
        for i in range(amount):
            (x, y) = self.position

            try:
                (x, y) = self.things[-1].position
            except Exception:
                pass

            self.things.append(Thing(x, y))

    def set_velocity(self, velocity):
        self.inputs.append(velocity)

    def inverse_velocity(self, velocity):
        (vx, vy) = velocity
        return (
            vx * -1,
            vy * -1
        )

    def find_invalid_moves(self):
        return (
            self.velocity,
            self.inverse_velocity(self.velocity))

    def find_valid_move(self):
        return next(
            # find earliest valid direction to turn
            (_input
                for _input
                in self.inputs
                if _input
                not in self.find_invalid_moves()),
            # default, dont turn
            self.velocity
        )

    def move(self):
        self.velocity = self.find_valid_move()
        self.inputs = []

        (vx, vy) = self.velocity
        (x, y) = self.position

        self.set_position(
            x + vx,
            y + vy
        )

        last_thing = None
        last_x = 0
        last_y = 0
        for thing in self.things:
            if last_thing is None:
                last_thing = thing
                (last_x, last_y) = thing.position
                (x, y) = self.position
                thing.set_position(x, y)
            else:
                (new_last_x, new_last_y) = thing.position
                thing.set_position(last_x, last_y)
                last_x = new_last_x
                last_y = new_last_y

class Apple(Thing):
    def __init__(self, x, y):
        super().__init__(x, y)

#snek_start_pos = math.floor(NBR_OF_CELLS/4)
apple_start_pos = math.floor(NBR_OF_CELLS/2)

class GameState:
    def __init__(self):
        self.snek = Snek(*get_new_apple_position(apple_start_pos, []))
        self.apple = Apple(apple_start_pos, apple_start_pos)

def random_pos_in_map():
    n = NBR_OF_CELLS
    return math.floor(random.uniform(0, n - 1))

def random_position():
    x = random_pos_in_map()
    y = random_pos_in_map()
    return (x, y)

class Game:
    def __init__(self):
        self.state = GameState()

    def get_score(self):
        return len(self.state.snek.things) - SNEK_START_LENGTH

    def update(self):
        self.state.snek.move()
        self.handle_out_of_bounds()
        self.handle_snek_collision()
        self.handle_apple_collision()

    def handle_out_of_bounds(self):
       snek = self.state.snek
       if(
            snek.x < 0 or
            snek.y < 0 or
            snek.x > NBR_OF_CELLS or
            snek.y > NBR_OF_CELLS
        ):
            # print("Outside!")
            raise GameOverException(snek.score)

    def check_collision(self, x1, y1, x2, y2):
        return x1 == x2 and y1 == y2

    def handle_snek_collision(self):
        snek = self.state.snek
        for thing in snek.things[1:]:
            has_collision = self.check_collision(
                snek.x, snek.y,
                thing.x, thing.y)
            if has_collision:
                #raise GameOverException(self.get_score())
                pass
                # print("self collision!")

    def handle_apple_collision(self):
        snek = self.state.snek
        apple = self.state.apple

        has_collision = self.check_collision(
            snek.x, snek.y,
            apple.x, apple.y)

        if has_collision:
            self.state.apple = Apple(
                *get_new_apple_position(apple.position, snek.things))
            snek.score += 1
            snek.add_things(1)

