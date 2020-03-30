import pyglet

from utils import add_key_listener

import snek_v2 as snek
from snek_v2 import GAME_SPEED, GAME_SIZE, THING_SIZE, GameOverException

white = (255, 255, 255)
red = (255, 50, 50)

def draw_thing(thing, color = white):
    x, y, size = thing.x, thing.y, thing.size

    parsed_color = ()
    for i in range(4):
        parsed_color += color

    pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP,
        ('v2f', (
            x, y,
            x + size, y,
            x + size, y + size,
            x, y + size
        )),
        ('c3B', parsed_color)
    )

class Game:
    def __init__(self):
        window_dimensions = (GAME_SIZE, GAME_SIZE)
        self.window = pyglet.window.Window(*window_dimensions)

        self.setup()

        @self.window.event
        def on_draw():
            self.window.clear()
            for thing in self.game.state.snek.things:
                draw_thing(thing)
            draw_thing(self.game.state.apple, red)

        pyglet.clock.schedule_interval(
            lambda dt: self.update(),
            1 / GAME_SPEED)
        pyglet.app.run()

    def update(self):
        try:
            self.game.update()
        except GameOverException as score:
            print(f"Game Over! Score: {score}")
            self.setup()

    def setup(self):
        self.game = snek.Game(use_bot=True)
        self.setup_input()

    def setup_input(self):
        snek = self.game.state.snek
        up = (0, 1)
        right = (1, 0)
        down = (0, -1)
        left = (-1, 0)
        add_key_listener("w", lambda: snek.set_velocity(up))
        add_key_listener("a", lambda: snek.set_velocity(left))
        add_key_listener("s", lambda: snek.set_velocity(down))
        add_key_listener("d", lambda: snek.set_velocity(right))

if __name__ == "__main__":
    Game()

