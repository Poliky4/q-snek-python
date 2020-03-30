import math
import random
import pyglet
from utils import add_key_listener, check_collision2

#GAME_SPEED = 2.50
#GAME_SPEED = 5.0
GAME_SPEED = 7.5

GAME_SIZE = 600

WIDTH = GAME_SIZE
HEIGHT = GAME_SIZE

NBR_OF_CELLS = 20
SNEK_SIZE = GAME_SIZE / NBR_OF_CELLS
SNEK_START_LENGTH = 3

def random_color():
    r = math.floor(random.uniform(50, 250))
    g = math.floor(random.uniform(50, 250))
    b = math.floor(random.uniform(50, 250))

    return (r, g, b)

def inverse_position(position):
    (x, y) = position
    return (x*-1, y*-1)

class Thing:
    def __init__(self, x, y, color=(255, 255, 255)):
        self.position = (x, y)

        color_thing = ()
        for i in range(4):
            color_thing += color

        self.shape = pyglet.graphics.vertex_list(
            4,
            ('v2f', self.calculate_positions(x, y)
            ),
            ('c3B', color_thing)
        )

    def draw(self):
        self.shape.draw(pyglet.graphics.GL_LINE_LOOP)

    def set_position(self, x, y):
        self.position = (x, y)
        self.shape.vertices = self.calculate_positions(x, y)

    def calculate_positions(self, x, y):
        return (
            x, y + SNEK_SIZE,
            x + SNEK_SIZE, y + SNEK_SIZE,
            x + SNEK_SIZE, y,
            x, y,
        )

    def update(self, dt):
        (x, y) = self.position
        self.set_position(x, y)

class Snek:
    def __init__(self, x, y):
        self.position = (x, y)
        self.velocity = (1, 0)
        self.things = []
        self.moves = []

        add_key_listener("w", self.set_velocity((0, 1)))
        add_key_listener("a", self.set_velocity((-1, 0)))
        add_key_listener("s", self.set_velocity((0, -1)))
        add_key_listener("d", self.set_velocity((1, 0)))

        self.add_things(SNEK_START_LENGTH)

    def add_things(self, amount):
        for i in range(amount):
            (x, y) = self.position

            try:
                (x, y) = self.things[-1].position
            except Exception:
                pass

            self.things.append(Thing(x, y, random_color()))

    def set_velocity(self, velocity):
        def _set_velocity():
            self.moves.append(velocity)
        return _set_velocity

    def draw(self):
        for thing in self.things:
            thing.draw()

    def find_valid_move(self):
        return next(
            (vel for vel in self.moves if vel not in (
                self.velocity,
                inverse_position(self.velocity))
            ),
            self.velocity
        )

    def update(self, dt):
        self.velocity = self.find_valid_move()
        self.moves = []

        (vx, vy) = self.velocity
        (x, y) = self.position

        self.position = (
            x + vx * SNEK_SIZE,
            y + vy * SNEK_SIZE
        )

        last_thing = None
        last_x = 0
        last_y = 0
        for thing in self.things:
            if last_thing == None:
                last_thing = thing
                (last_x, last_y) = thing.position
                (x, y) = self.position
                thing.set_position(x, y)
            else:
                (new_last_x, new_last_y) = thing.position
                thing.set_position(last_x, last_y)
                last_x = new_last_x
                last_y = new_last_y

red = (0, 200, 0)
class Apple(Thing):
    def __init__(self, x, y):
        super().__init__(x, y, red)

class Label:
    def __init__(self, text, x=0, y=0, onUpdate=lambda: None):
        self.label = pyglet.text.Label(
            text,
            x=x,
            y=y
        )
        self.onUpdate = onUpdate

    def draw(self):
        self.label.draw()

    def update(self, dt):
        self.label.text = self.onUpdate()

def get_random_position():
    return SNEK_SIZE * math.floor(random.uniform(0, NBR_OF_CELLS - 1))

def get_all_positions():
    positions = []
    for y in range(NBR_OF_CELLS):
        for x in range(NBR_OF_CELLS):
            positions.append((x*SNEK_SIZE, y*SNEK_SIZE))
    return positions

all_positions = set(get_all_positions())
def get_random_position2(apple, things):
    taken_positions = [thing.position for thing in things]
    possible_positions = list(
        all_positions -
        set(taken_positions) -
        set([apple.position])
    )
    return random.choice(possible_positions)

def check_collision(a, b):
    (a_x, a_y) = a.position
    (b_x, b_y) = b.position

    return check_collision2(
        x1 = a_x,
        y1 = a_y,
        x2 = b_x,
        y2 = b_y,
        distance = SNEK_SIZE)

class SelfCollisionException(Exception):
    def __init__(self):
        pass
class OutOfBoundsException(Exception):
    def __init__(self):
        pass

if __name__ == '__main__':
    game_window = pyglet.window.Window(WIDTH, HEIGHT)
    game_objects = []

    apples = [Apple(
        SNEK_SIZE * math.floor(NBR_OF_CELLS/2),
        SNEK_SIZE * math.floor(NBR_OF_CELLS/2),
    )]

    snek = Snek(
        SNEK_SIZE * math.floor(NBR_OF_CELLS/4),
        SNEK_SIZE * math.floor(NBR_OF_CELLS/4),
    )

    get_score = lambda: len(snek.things) - SNEK_START_LENGTH
    make_score_label_text = lambda: f'Score: {get_score()}'
    score_label = Label(
        make_score_label_text(),
        onUpdate=lambda: make_score_label_text()
    )

    game_objects.append(apples[0])
    game_objects.append(snek)
    # game_objects.append(score_label)

    @game_window.event
    def on_draw():
        game_window.clear()
        for obj in game_objects:
            obj.draw()

    def update(dt):
        if(check_collision(snek.things[0], apples[0])):
            snek.add_things(1)
            random_pos = get_random_position2(apples[0], snek.things)
            apples[0].set_position(*random_pos)

        for obj in game_objects:
            if(hasattr(obj, 'update')):
                obj.update(dt)
        (x, y) = snek.position
        if(
            x < 0 or
            y < 0 or
            x + SNEK_SIZE > GAME_SIZE or
            y + SNEK_SIZE > GAME_SIZE
        ):
            raise OutOfBoundsException
        for thing in snek.things[1:]:
            if(check_collision(snek, thing)):
                print("crash?")
                raise SelfCollisionException

    def game_over():
        print("Game Over")
        print(get_score())
        snek.things = snek.things[:3]
        # pyglet.app.exit()

    def game_loop(dt):
        try:
            update(dt)
        except Exception:
            game_over()

    pyglet.clock.schedule_interval(update, 1 / GAME_SPEED)
    pyglet.app.run()

