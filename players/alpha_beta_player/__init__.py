import abstract
import players.min_max_player as mmp
from utils import MiniMaxWithAlphaBetaPruning, INFINITY


class Player(mmp.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        mmp.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.searcher = MiniMaxWithAlphaBetaPruning(self.utility,
                                             self.color,
                                             self.no_more_time,
                                             self.selective_deepening_criterion)

    def search(self, state, depth):
        return self.searcher.search(state, depth, -INFINITY, INFINITY, True)

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'alpha_beta')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
