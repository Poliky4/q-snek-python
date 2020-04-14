import os
clear = lambda: os.system('clear')

import rx
from rx.scheduler import EventLoopScheduler

import snek
from snek import ACTIONS, FPS, NBR_OF_CELLS, GameOverException

import bot
from q_bot import QBot
q_bot = QBot()

USE_Q_BOT = True

make_clean_board = lambda: [[
    ' ' for x in range(NBR_OF_CELLS)
] for y in range(NBR_OF_CELLS)]

MAX_ATTEMPTS = 10000

class HeadlessSnek:
    def __init__(self):
        self.attempts = 0
        self.average_score = 0
        self.best_score = 0
        self.worst_score = None
        self.start_new_game()

        scheduler = EventLoopScheduler()
        scheduler.schedule_periodic(
            FPS / 1000,
            lambda state: self.update()
        )

    def start_new_game(self):
        self.game = snek.Game()
        self.attempts += 1

    def update_bot(self):
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

    def update(self):
        try:
            action = None
            self.update_bot()
            self.game.update()
            # self.draw()
        except GameOverException as score:
            if USE_Q_BOT:
                q_bot.trigger_game_over(self.game.state.snek)

            score = int(str(score))
            self.best_score = score if score > self.best_score else self.best_score

            self.worst_score = score if self.worst_score is None else self.worst_score
            self.worst_score = score if score < self.worst_score else self.worst_score

            self.average_score = (self.attempts * self.average_score + score) / (self.attempts + 1)

            if True:
                msg = 'Game Over!'
                msg += f' A: {str(self.attempts).ljust(4)}'
                msg += f' S: {str(score).ljust(4)}'
                msg += f' B: {str(self.best_score).ljust(4)}'
                msg += f' W: {str(self.worst_score).ljust(4)}'
                msg += f' A: {str(self.average_score).ljust(4)}'
                print(msg)

            if self.attempts < MAX_ATTEMPTS:
                self.start_new_game()
            else:
                if USE_Q_BOT:
                    q_bot.show_vis_data()

    def draw(self):
        snek = self.game.state.snek
        apple = self.game.state.apple

        clear()

        board = make_clean_board()

        board[apple.y][apple.x] = 'X'
        for thing in snek.things:
            board[thing.y][thing.x] = 'O'

        for row in board:
            print("".join(row))

if __name__ == "__main__":
    HeadlessSnek()
    input()

