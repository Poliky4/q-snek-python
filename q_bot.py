import math
import random

import matplotlib.pyplot as plt

from snek import ACTIONS, NBR_OF_CELLS
UP = ACTIONS.UP
RIGHT = ACTIONS.RIGHT
DOWN = ACTIONS.DOWN
LEFT = ACTIONS.LEFT

up = ACTIONS.up
right = ACTIONS.right
down = ACTIONS.down
left = ACTIONS.left

actions = [
    UP,
    RIGHT,
    DOWN,
    LEFT
]

action_map = (
    (UP, ACTIONS.up),
    (RIGHT, ACTIONS.right),
    (DOWN, ACTIONS.down),
    (LEFT, ACTIONS.left),
)

def map_action(action):
    return (
        UP if action == up else
        up if action == UP else
        RIGHT if action == right else
        right if action == RIGHT else
        DOWN if action == down else
        down if action == DOWN else
        LEFT if action == left else
        left if action == LEFT else print("Error")
    )

class Rewards:
    apple = 100
    lose = -1000

MAX_TRIALS = 1000
SAMPLE_EVERY = 1

class QBot:
    def __init__(self):
        self.Q_table = dict()
        self.gamma = 0.95 #0.8 # discounted rewards
        self.alpha = 0.1 # learning rate
        self.frame_buffer = []
        self.episode_frame_count = 0
        self.trials = 0
        self.last_apple_position = None
        self.last_snek_position = None
        self.random_moves = 0
        self.random_chance = 0
        self.vis_data = {}
        self.vis_data['episodes'] = []
        self.vis_data['scores'] = []
        self.vis_data['rules'] = []

    def show_vis_data(self):
        data = self.vis_data
        plt.plot(data['episodes'], data['scores'], label="Score")
        plt.plot(data['episodes'], data['rules'], label="Rules")
        plt.legend(loc=4)
        plt.show()

    def make_vis_data(self, snek):
        if self.trials % SAMPLE_EVERY == 0:
            self.vis_data['episodes'].append(self.trials)
            self.vis_data['scores'].append(snek.score)
            self.vis_data['rules'].append(len(self.Q_table))

    def make_env(self, snek, apple):
        return (
            #self.get_distance_to_edge(snek),
            self.make_local_map(snek, apple),
            #self.get_distance2(snek, apple),
            #snek.velocity
        )

    def make_local_map(self, snek, apple):
        return (
            (LEFT, self.check_direction(snek, apple, left)),
            (RIGHT, self.check_direction(snek, apple, right)),
            (UP, self.check_direction(snek, apple, up)),
            (DOWN, self.check_direction(snek, apple, down))
        )

    def check_direction(
        self,
        snek, apple,
        direction,
        position = None
    ):
        if position is None:
            position = snek.position

        d = map_action(direction)

        (vx, vy) = snek.velocity
        (sx, sy) = position
        (ax, ay) = apple.position
        (dx, dy) = direction
        new_position = (
            sx + dx,
            sy + dy
        )
        (nx, ny) = new_position

        """
        is_direction_right = map_action(direction) == RIGHT
        is_going_right = vx == 1
        is_apple_right = sx < ax
        if is_direction_right and is_going_right and is_apple_right:
                    return "APPLE THIS WAY"
        """

        if (
            position is snek.position and
            self.is_outside(new_position)):
            #return None
            return "WALL"
        else:
            if (d is UP or d is DOWN) and ny == ay:
                return "APPLE!"
            elif (d is RIGHT or d is LEFT) and nx == ax:
                return "APPLE!"
            elif self.is_outside(new_position):
                return None
            else:
                return self.check_direction(snek, apple, direction,
                    position=new_position)

    def is_outside(self, position):
        (x, y) = position
        return not 0 <= x <= NBR_OF_CELLS or not 0 <= y <= NBR_OF_CELLS

    def next_step(self, state):
        apple = state.apple
        snek = state.snek

        if snek.position == self.last_apple_position:
            # snek eat apple
            self.reward_snek(Rewards.apple)
            self.end_episode()

        self.last_apple_position = apple.position
        self.last_snek_position = snek.position
        action_to_be_taken = self.get_action(state)

        config = (
            self.make_env(snek, apple),
            action_to_be_taken
        )

        self.frame_buffer.append(config)
        self.episode_frame_count += 1

        return action_to_be_taken

    def get_possible_actions(self, snek, cheat=False):
        possible_actions = [
            action
            for action
            in actions
            if map_action(action) != snek.inverse_velocity(
                snek.velocity)
            # and not self.out_of_bounds(snek, action)
        ]
        """
        if cheat is True:
            old_length = len(possible_actions)
            possible_actions = [
                action
                for action
                in possible_actions if self.check_direction(
                    snek, map_action(action)) is None
            ]
            if old_length != len(possible_actions):
                print("CHEATING", old_length, len(possible_actions))
        if not possible_actions:
            return actions
        """
        return possible_actions

    def get_action(self, game_state):
        snek = game_state.snek

        possible_actions = self.get_possible_actions(snek)

        chance_initial = 60
        chance_adjuster = self.trials
        chance = max(1, chance_initial - chance_adjuster)
        self.random_chance = chance / 100
        take_random_action = random.choice([
            *[True for i in range(chance)],
            *[False for i in range(200)]])
        if take_random_action:
            self.random_moves += 1
            #print("Going random!")
            #return random.choice(possible_actions)
            return random.choice(
                self.get_possible_actions(snek, cheat=True))

        env = self.make_env(game_state.snek, game_state.apple)
        rewards = [
            (action, self.get_Q(env, action))
            for action
            in possible_actions
        ]
        sorted_actions = sorted(
            rewards,
            key=lambda r: r[1],
            reverse=True
        )
        (best_action, best_score) = sorted_actions[0]
        best_actions = [
            action
            for action
            in sorted_actions
            if action[1] == best_score
        ]
        if len(best_actions) > 1:
            (random_action, _) = random.choice(best_actions)
            return random_action
        # print("best action", rewards)
        return best_action

    def reward_snek(self, reward):
        min_frame_size = 5
        frame_size = max(min_frame_size, self.episode_frame_count)

        i = len(self.frame_buffer) - 2;
        while(i >= 0 and frame_size > 0):
            (state, action) = self.frame_buffer[i]

            (future_state, _) = self.frame_buffer[i+1]
            optimal_future_value = max([
                self.get_Q(future_state, action)
                for action in actions])
            update_value = self.alpha * (
                reward +
                self.gamma * optimal_future_value -
                self.get_Q(state, action)
            )
            self.set_Q(state, action, update_value)

            frame_size -= 1
            i -= 1

        self.frame_buffer = self.frame_buffer[-min_frame_size:]
        self.episode_frame_count = 0

    def trigger_game_over(self, snek):
        self.reward_snek(Rewards.lose)
        self.make_vis_data(snek)
        self.end_episode()
        self.trials += 1

        #if self.trials >= MAX_TRIALS:
            #self.show_vis_data()

    def end_episode(self):
        self.frame_buffer = [] # ?
        self.episode_frame_count = 0 # ?

    def clamp(self, mi, ma, val):
        return max(mi, min(val, ma))
    def normalize(self, num):
        return self.clamp(-1, 1, num)
    def get_distance(self, ax, ay, bx, by):
        return math.sqrt(math.pow(ax-bx, 2) + math.pow(ay-by, 2))

    def get_distance2(self, a, b):
        (ax, ay) = a.position
        (bx, by) = b.position
        (vx, vy) = (ax-bx, ay-by)
        return (
            self.normalize(vx),
            self.normalize(vy)
        )

    def get_distance_to_edge(self, snek):
        (snek_x, snek_y) = snek.position
        left = snek_x
        right = NBR_OF_CELLS - snek_x
        down = snek_y
        up = NBR_OF_CELLS - snek_y

        close_to_wall = ()

        if left == 0:
            close_to_wall += (LEFT,)
        if right == 0:
            close_to_wall += (RIGHT,)
        if up == 0:
            close_to_wall += (UP,)
        if down == 0:
            close_to_wall += (DOWN,)

        return close_to_wall

    def get_Q(self, state, action):
        config = (state, action)
        if config not in self.Q_table:
            return 0
        else:
            return self.Q_table[config]

    def set_Q(self, state, action, reward):
        config = (state, action)
        if config not in self.Q_table:
            self.Q_table[config] = 0
        else:
            self.Q_table[config] += reward

    def out_of_bounds(self, snek, action):
        (sx, sy) = snek.position
        (vx, vy) = action
        (new_x, new_y) = (sx + vx, sy + vy)
        is_outside = (new_x == 0 or
            new_y == 0 or
            new_x == NBR_OF_CELLS or
            new_y == NBR_OF_CELLS)
        return is_outside

