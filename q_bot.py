import math
import random

from snek import ACTIONS, NBR_OF_CELLS
UP = ACTIONS.UP
RIGHT = ACTIONS.RIGHT
DOWN = ACTIONS.DOWN
LEFT = ACTIONS.LEFT

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

class Rewards:
    apple = 300
    move_closer = 10
    move_away = 10
    lose = 100

class QBot:
    def __init__(self):
        self.Q_table = dict()
        self.gamma = 0.8 # discounted rewards
        self.alpha = 0.1 # learning rate
        self.frame_buffer = []
        self.episode_frame_count = 0
        self.trials = 0
        self.last_apple_position = None
        self.last_snek_position = None

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

    def get_action(self, game_state):
        snek = game_state.snek
        possible_actions = [
            action for action in actions if action not in snek.find_invalid_moves()
        ]
        take_random_action = random.choice([
            *[True for i in range(max(1, 30 - self.trials))],
            *[False for i in range(100)]])
        if take_random_action:
            # print("Going random!")
            return random.choice(possible_actions)

        env = (
            self.get_distance_to_edge(game_state.snek),
            self.get_distance2(game_state.snek, game_state.apple),
            game_state.snek.velocity
        )
        rewards = [(action, self.get_Q(env, action)) for action in possible_actions]
        sorted_actions = sorted(rewards, key=lambda r: r[1])
        (best_action, best_score) = sorted_actions[0]
        best_actions = [action for action in sorted_actions if action[1] is best_score]
        if len(best_actions) > 1:
            (random_action, _) = random.choice(best_actions)
            return random_action
        # print("best action", rewards)
        return best_action

    def reward_snek(self, reward, was_successful):
        was_successful = not was_successful
        min_frame_size = 5 # eh?
        # theta = 1 # tolerable deviation
        frame_size = self.episode_frame_count
        # TODO: math.min
        if frame_size < min_frame_size: frame_size = min_frame_size

        i = len(self.frame_buffer) - 2;
        while(i >= 0 and frame_size > 0):
            config = self.frame_buffer[i]
            (state, action) = config
            reward_for_state = reward - 0 # - distance

            if was_successful is not True:
                reward_for_state = -reward_for_state

            # (future_state, _) = frame_buffer[i+1]
            update_value = self.alpha*(reward_for_state - self.get_Q(state, action))
            # print(f"Setting reward {update_value} for action {action}")
            self.set_Q(state, action, update_value)

            frame_size -= 1
            i -= 1

        self.frame_buffer = self.frame_buffer[:]
        self.episode_frame_count = 0

    def trigger_game_over(self):
        self.reward_snek(Rewards.lose, False)
        self.episode_frame_count = 0
        self.trials += 1
        print("Game Over", self.trials, len(self.Q_table))

    def clamp(self, mi, ma, val):
        return max(mi, min(val, ma))
    def normalize(self, num):
        return self.clamp(-1, 1, num)

    # cartesian?
    def get_distance(self, ax, ay, bx, by):
        return math.sqrt(math.pow(ax-bx, 2) + math.pow(ay-by, 2))

    # (vx, vy)
    # ([-1,0,1], [-1,0,1])
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

        return min(left, right, down, up)

    def get_distance_reward(self, reward, distance):
        percentage = (NBR_OF_CELLS - distance) / NBR_OF_CELLS
        # print("distance reward %", distance, percentage)
        return reward * percentage

    def next_step(self, state):
        apple = state.apple
        snek = state.snek

        # print("Q_table", self.Q_table)
        if self.last_apple_position is not None:
            # snek eat apple
            if snek.position == apple.position:
                print("APPLEZ!")
                self.reward_snek(Rewards.apple, True)
            else:
                # snek move closer to apple
                old_distance = self.get_distance(
                    *self.last_snek_position,
                    *self.last_apple_position)
                new_distance = self.get_distance(
                    *snek.position,
                    *apple.position)

                getting_closer = new_distance < old_distance
                # print(f"old_distance - new_distance", old_distance - new_distance)
                # print("closer" if getting_closer is True else "away")
                if getting_closer:
                    #score = Rewards.move_closer + Rewards.move_closer * 
                    reward = self.get_distance_reward(
                            Rewards.move_closer, new_distance)
                    self.reward_snek(reward, True)
                else:
                    reward = self.get_distance_reward(
                            Rewards.move_away, new_distance)
                    self.reward_snek(reward, False)

        self.last_apple_position = apple.position
        self.last_snek_position = snek.position
        action_to_be_taken = self.get_action(state)

        # replace this config
        # with something less specific
        # like (is_above, is_right, velocity)
        # but it's also going to need to learn
        # not to crash into self or wall
        # so that information is going in here
        # like check_future(has_crash or out_of_bounds) = bad snek
        config = ((
                self.get_distance_to_edge(snek),
                self.get_distance2(snek, apple),
                snek.velocity
            ),
            action_to_be_taken
        )

        self.frame_buffer.append(config)
        self.episode_frame_count += 1

        return action_to_be_taken

