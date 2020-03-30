import math
import random
from utils import check_collision2

# GAME_SPEED = 7.5
GAME_SPEED = 30
FPS = 1 / GAME_SPEED

GAME_SIZE = 600

NBR_OF_CELLS = 20

THING_SIZE = GAME_SIZE / NBR_OF_CELLS

SNEK_START_LENGTH = 3

class GameOverException(Exception):
    def __init__(self):
        pass

def get_all_positions():
    positions = []
    for y in range(NBR_OF_CELLS):
        for x in range(NBR_OF_CELLS):
            positions.append((x*THING_SIZE, y*THING_SIZE))
    return positions
all_positions = set(get_all_positions())
def get_new_apple_position(old_apple, things):
    things_positions = [thing.position for thing in things]
    possible_positions = list(
        all_positions -
        set(things_positions) -
        set([old_apple.position])
    )
    return random.choice(possible_positions)

class Thing:
    def __init__(self, x, y):
        self.position = (x, y)
        self.x = x
        self.y = y
        self.size = THING_SIZE

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
            x + vx * THING_SIZE,
            y + vy * THING_SIZE
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

snek_start_pos = THING_SIZE * math.floor(NBR_OF_CELLS/4)
apple_start_pos = THING_SIZE * math.floor(NBR_OF_CELLS/2)
class GameState:
    def __init__(self):
        self.snek = Snek(snek_start_pos, snek_start_pos)
        self.apple = Apple(apple_start_pos, apple_start_pos)

def random_pos_in_map():
    n = NBR_OF_CELLS
    return THING_SIZE * math.floor(random.uniform(0, n - 1))

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
            snek.x + snek.size > GAME_SIZE or
            snek.y + snek.size > GAME_SIZE
        ):
            # print("Outside!")
            raise GameOverException(self.get_score())

    def handle_snek_collision(self):
        snek = self.state.snek
        for thing in snek.things[1:]:
            has_collision = check_collision2(
                snek.x, snek.y,
                thing.x, thing.y,
                snek.size)
            if has_collision:
                # print("self collision!")
                raise GameOverException(self.get_score())

    def handle_apple_collision(self):
        snek = self.state.snek
        apple = self.state.apple

        has_collision = check_collision2(
            snek.x, snek.y,
            apple.x, apple.y,
            apple.size
        )

        if has_collision:
            self.state.apple = Apple(
                *get_new_apple_position(apple, snek.things))
            snek.add_things(1)

