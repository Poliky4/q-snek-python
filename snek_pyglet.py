import pyglet

from utils import add_key_listener

import snek
from snek import GAME_SPEED,NBR_OF_CELLS, GameOverException, ACTIONS

import bot
from q_bot import QBot
q_bot = QBot()

USE_BOT = True
# USE_BOT = False

# USE_Q_BOT = False
USE_Q_BOT = True

GAME_SIZE = 600
THING_SIZE = GAME_SIZE / NBR_OF_CELLS

white = (255, 255, 255)
red = (255, 50, 50)

def draw_thing(thing, color = white):
    x, y = thing.x, thing.y

    x = x * THING_SIZE
    y = y * THING_SIZE

    parsed_color = ()
    for i in range(4):
        parsed_color += color

    pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP,
        ('v2f', (
            x, y,
            x + THING_SIZE, y,
            x + THING_SIZE, y + THING_SIZE,
            x, y + THING_SIZE
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
            self.update_bot()
            self.game.update()
        except GameOverException as score:
            print(f"Game Over! Score: {score}")

            if USE_BOT is True and USE_Q_BOT is True:
                q_bot.trigger_game_over()

            self.setup()

    def update_bot(self):
        if USE_BOT:
            snek = self.game.state.snek

            action = None

            if USE_Q_BOT:
                action = q_bot.next_step(self.game.state)
            else:
                action = bot.play(self.game.state)

            if action is ACTIONS.UP:
                snek.set_velocity(ACTIONS.up)
            elif action is ACTIONS.RIGHT:
                snek.set_velocity(ACTIONS.right)
            elif action is ACTIONS.DOWN:
                snek.set_velocity(ACTIONS.down)
            elif action is ACTIONS.LEFT:
                snek.set_velocity(ACTIONS.left)

    def setup(self):
        self.game = snek.Game()
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

