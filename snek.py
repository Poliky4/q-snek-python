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

NBR_OF_CELLS = 20
SNEK_SIZE = GAME_SIZE / NBR_OF_CELLS
SNEK_START_LENGTH = 3

game_window = pyglet.window.Window(WIDTH, HEIGHT)
main_batch = pyglet.graphics.Batch()

game_objects = []

class Thing:
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

    def set_position(self, x, y):
        self.position = (x, y)
        self.circle.vertices = self.calculate_positions(x, y)

    def calculate_positions(self, x, y):
        return (
            # top left
            x, y + SNEK_SIZE,
            x, y + SNEK_SIZE,
            # top
            # top right
            x + SNEK_SIZE, y + SNEK_SIZE,
            x + SNEK_SIZE, y + SNEK_SIZE,
            # right
            # bottom right
            x + SNEK_SIZE, y,
            x + SNEK_SIZE, y,
            # bottom
            # bottom left
            x, y,
            x, y,
            # left
        )

    def update(self, dt):
        (x, y) = self.position
        self.set_position(x, y)

class Snek:
    def __init__(self, x, y):
        self.position = (x, y)
        self.velocity = (1, 0)
        self.things = []
        #self.last_velocity = None

        inputs.add_key_listener(
            "w", self.set_velocity((0, 1)))
        inputs.add_key_listener(
            "a", self.set_velocity((-1, 0)))
        inputs.add_key_listener(
            "s", self.set_velocity((0, -1)))
        inputs.add_key_listener(
            "d", self.set_velocity((1, 0)))

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
        def _set_velocity():
            if self.velocity[0] == velocity[0]: return
            if self.velocity[1] == velocity[1]: return
            # if velocity == self.last_velocity: raise "blaa"
            # self.last_velocity = velocity
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

red = (0, 200, 0)
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
    return SNEK_SIZE * math.floor(random.uniform(0, NBR_OF_CELLS - 1))

def check_collision(a, b):
    (a_x, a_y) = a.position
    (b_x, b_y) = b.position
    x_distance = abs(a_x - b_x)
    y_distance = abs(a_y - b_y)

    return x_distance < SNEK_SIZE and y_distance < SNEK_SIZE

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

    main_batch.draw()



def update(dt):

    if(check_collision(snek.things[-1], apples[0])):
        x = get_random_position()
        y = get_random_position()
        apples[0].set_position(x, y)
        snek.add_things(1)

    for obj in game_objects:
        if(hasattr(obj, 'update')):
            obj.update(dt)

    if(check_collision(snek.things[-1], apples[0])):
        x = get_random_position()
        y = get_random_position()
        apples[0].set_position(x, y)
        snek.add_things(1)

    (x, y) = snek.position
    if(
        x < 0 or
        y < 0 or
        x + SNEK_SIZE > GAME_SIZE or
        y + SNEK_SIZE > GAME_SIZE
    ):
        raise Exception("outside")

    for thing in snek.things[:-2]:
        if(check_collision(snek, thing)):
            raise Exception("game over!")

def game_loop(dt):
    try:
        update(dt)
    except Exception:
        print("Game Over")
        print(len(snek.things) - SNEK_START_LENGTH)
        pyglet.app.exit()

if __name__ == '__main__':
    pyglet.clock.schedule_interval(game_loop, 1 / GAME_SPEED)
    pyglet.app.run()

