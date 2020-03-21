import math
import random
from utils import Input
import pyglet

inputs = Input()

#GAME_SPEED = 2.50
#GAME_SPEED = 5.0
GAME_SPEED = 7.5

GAME_SIZE = 600

WIDTH = GAME_SIZE
HEIGHT = GAME_SIZE

NBR_OF_CELLS = 50
SNEK_SIZE = GAME_SIZE / NBR_OF_CELLS

game_window = pyglet.window.Window(WIDTH, HEIGHT)
main_batch = pyglet.graphics.Batch()

game_objects = []

#SCALING_FACTOR = 1.4
SCALING_FACTOR = 1
class Thing:
    position = (0, 0)

    def __init__(self, x, y, color=(255, 255, 255)):
        self.position = (x, y)

        color_thing = ()
        for i in range(8):
            color_thing += color

        self.circle = pyglet.graphics.vertex_list(
            8,
            ('v2f', self.calculate_positions(x, y)
            ),
            ('c3B', color_thing)
        )

    def draw(self):
        self.circle.draw(pyglet.graphics.GL_LINE_LOOP)

    def calculate_positions(self, x, y):
        s = SNEK_SIZE / 2
        s2 = SNEK_SIZE * 0.95
        f = SCALING_FACTOR

        return (
            # top left
            x - s, y + s,
            # top
            x, y + s2,
            # top right
            x + s, y + s,
            # right
            x + s2, y,
            # bottom right
            x + s, y - s,
            # bottom
            x, y - s2,
            # bottom left
            x - s, y - s,
            # left
            x - s2, y
        )

    def set_position(self, x, y):
        self.position = (x, y)
        self.circle.vertices = self.calculate_positions(x, y)

    def update(self, dt):
        (x, y) = self.position
        self.set_position(x, y)

"""
        return (
            # top left
            x - s, y + s,
            # top
            x, y + s*f,
            # top right
            x + s, y + s,
            # right
            x + s*f, y,
            # bottom right
            x + s, y - s,
            # bottom
            x, y - s*f,
            # bottom left
            x - s, y - s,
            # left
            x - s*f, y
        )
"""

class Snek:
    position = (0, 0)
    velocity = (1, 1)
    things = []

    def __init__(self, x, y):
        self.position = (x, y)

        inputs.add_key_listener(
            "w", self.set_velocity((0, 1)))
        inputs.add_key_listener(
            "a", self.set_velocity((-1, 0)))
        inputs.add_key_listener(
            "s", self.set_velocity((0, -1)))
        inputs.add_key_listener(
            "d", self.set_velocity((1, 0)))

        self.add_things(3)

    def add_things(self, amount):
        for i in range(amount):
            (x, y) = self.position

            try:
                (x, y) = self.things[0].position
            except Exception:
                pass

            self.things.append(Thing(x, y))

    def set_velocity(self, velocity):
        def _set_velocity():
            if self.velocity[0] == velocity[0]: return
            if self.velocity[1] == velocity[1]: return
            self.velocity = velocity
        return _set_velocity

    def draw(self):
        for thing in self.things:
            thing.draw()

    def update(self, dt):
        (vx, vy) = self.velocity
        (x, y) = self.position
        self.position = (
            x + vx * SNEK_SIZE,
            y + vy * SNEK_SIZE
        )

        last_thing = None
        last_x = 0
        last_y = 0
        for thing in reversed(self.things):
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

red = (200, 0, 0)
def Apple(x, y):
    return Thing(x, y, red)

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
    return SNEK_SIZE * random.uniform(1, NBR_OF_CELLS - 1)

snek = Snek(SNEK_SIZE * 10, SNEK_SIZE * 20)
apples = [Apple(
    get_random_position(),
    get_random_position()
)]

make_snek_label_text = lambda position: f'x:{math.floor(position[0])} y:{math.floor(position[1])}'
snek_label = Label(
    make_snek_label_text(snek.position),
    onUpdate=lambda: make_snek_label_text(snek.position)
)

make_apple_label_text = lambda position: f'apple x:{math.floor(position[0])} y:{math.floor(position[1])}'
apple_label = Label(
    make_apple_label_text(apples[0].position),
    onUpdate=lambda: make_apple_label_text(apples[0].position),
    y=20
)

game_objects.append(apples[0])
game_objects.append(snek)
# game_objects.append(snek_label)
# game_objects.append(apple_label)

@game_window.event
def on_draw():
    game_window.clear()

    for obj in game_objects:
        obj.draw()

    main_batch.draw()

def update(dt):

    if(check_collision(snek.things[-1], apples[0])):
        x = get_random_position()
        y = get_random_position()
        apples[0].set_position(x, y)
        snek.add_things(1)

    (snek_x, snek_y) = snek.position
    (apple_x, apple_y) = apples[0].position
    if(snek_x == apple_x and snek_y == apple_y):
        pass

    for obj in game_objects:
        if(hasattr(obj, 'update')):
            obj.update(dt)

def check_collision(a, b):
    (a_x, a_y) = a.position
    (b_x, b_y) = b.position
    x_distance = abs(a_x - b_x)
    y_distance = abs(a_y - b_y)

    return x_distance < SNEK_SIZE and y_distance < SNEK_SIZE

if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1 / GAME_SPEED)
    pyglet.app.run()

