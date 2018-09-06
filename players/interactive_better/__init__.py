import abstract
from Reversi.consts import *
import copy
import players.better_player as bp
from utils import INFINITY


class Player(bp.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        bp.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)

    def get_move(self, game_state, possible_moves):
        print('Available moves:')
        maxx = -INFINITY
        for i, move in enumerate(possible_moves):
            h = self.get_h(game_state, move)
            maxx = max(maxx, h)
            print("({}) {} - {}".format(i, str(move), h))
        print("max: {}".format(maxx))
        while True:
            # Trying to get the next move index from the user.
            idx = input('Enter the index of your move: ')
            try:
                idx = int(idx)
                if idx < 0 or idx >= len(possible_moves):
                    raise ValueError
                return possible_moves[idx]
            except ValueError:
                # Ignoring
                pass

    def get_h(self, game_state, move):
        new_state = copy.deepcopy(game_state)
        new_state.perform_move(move[0], move[1])
        return self.utility(new_state)

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'interactive')

# c:\python35\python run_game.py 3 3 3 y interactive interactive