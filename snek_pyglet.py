import random
import pyglet

from utils import add_key_listener

import snek
from snek import GAME_SPEED,NBR_OF_CELLS, GameOverException, ACTIONS

import bot
from q_bot import QBot
q_bot = QBot()

RENDER = True
USE_BOT = False
USE_BOT = True

USE_Q_BOT = False
USE_Q_BOT = True

GAME_SIZE = 600
THING_SIZE = GAME_SIZE / (NBR_OF_CELLS + 1)

white = (255, 255, 255)
red = (255, 50, 50)
_r = lambda: random.randrange(50, 250)
random_color = lambda: (_r(), _r(), _r())

class Bool:
    def __init__(self, is_true = True):
        self.is_true = is_true

    def toggle(self):
        self.is_true = not self.is_true

SHOW_STATS = Bool(True)
add_key_listener("s", SHOW_STATS.toggle)

def draw_thing(thing, color = None):
    if color is None: color = random_color()

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
        self.labels = []

        self.average_score = 0
        self.best_score = 0
        self.scores_to_keep = 50
        self.last_scores = []
        self.current_average = 0

        self.setup()
        self.setup_labels()

        @self.window.event
        def on_draw():
            self.window.clear()
            for thing in self.game.state.snek.things:
                draw_thing(thing)
            draw_thing(self.game.state.apple, red)
            if SHOW_STATS.is_true:
                self.update_and_draw_labels()

        pyglet.clock.schedule_interval(
            lambda dt: self.update(),
            1 / GAME_SPEED)
        pyglet.app.run()

    def make_state_label(self):
        make_state = lambda: q_bot.make_env(
            self.game.state.snek, self.game.state.apple)

        self.make_label(
                on_update = lambda: f"map: {make_state()[0]}")

    def setup_labels(self):
        if USE_Q_BOT:
            # self.make_state_label()
            self.make_label(
                on_update = lambda: f"random chance: {round(q_bot.random_chance*100)}%")
            self.make_label(
                on_update = lambda: f"random: {q_bot.random_moves}")
            self.make_label(
                on_update = lambda: f"trials: {q_bot.trials}")
            self.make_label(
                on_update = lambda: f"rules: {len(q_bot.Q_table)}")
        self.make_label(
            on_update = lambda: f"average last {len(self.last_scores)}: {round(self.current_average, 3)}")
        self.make_label(
            on_update = lambda: f"average score: {round(self.average_score, 3)}")
        self.make_label(
            on_update = lambda: f"best score: {self.best_score}")
        self.make_label(
            on_update = lambda: f"score: {self.game.state.snek.score}")
        self.make_label(
            on_update = lambda: f"use_bot: {q_bot.use_bot}")

    def make_label(self, text = "", on_update = lambda: None):
        y = 20 * (len(self.labels) + 1)
        x = 10

        label = pyglet.text.Label(
            text,
            x=x,
            y=y
        )

        def update(text):
            if text is not None:
                label.text = text

        self.labels.append((
            label,
            lambda: update(on_update())
        ))

    def update_and_draw_labels(self):
        for (label, update_label) in self.labels:
            update_label()
            label.draw()

    def handle_game_over(self):
        score = self.game.state.snek.score
        # print(f"Game Over! Score: {score}")

        if USE_BOT is True and USE_Q_BOT is True:
            q_bot.trigger_game_over(self.game.state.snek)

        if score > self.best_score:
            self.best_score = score

        self.average_score = (
            q_bot.trials * self.average_score + score
        ) / (q_bot.trials + 1)

        self.last_scores = [
            *self.last_scores[-self.scores_to_keep-1:],
            score
        ]
        self.current_average = sum(self.last_scores) / len(self.last_scores)

        self.setup()

    def update(self):
        try:
            self.update_bot()
            self.game.update()
        except GameOverException:
            self.handle_game_over()

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

