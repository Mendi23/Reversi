import abstract
import players.better_player as bp
from utils import MiniMaxAlgorithm, ExceededTimeError, INFINITY


class Player(bp.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        bp.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.searcher = MiniMaxAlgorithm(self.utility,
                                         self.color,
                                         self.no_more_time,
                                         self.selective_deepening_criterion)

    def get_move_logic(self, game_state, possible_moves):

        best_move = possible_moves[0]
        if len(possible_moves) == 1:
            return best_move

        depth = 1

        try:
            while not self.no_more_time():
                next_move = self.search(game_state, depth)
                best_move = next_move[1] if next_move[1] else best_move
                if next_move[1] and next_move[0] == INFINITY:
                    return best_move
                depth += 1
        except ExceededTimeError:
            pass

        return best_move

    def search(self, state, depth):
        return self.searcher.search(state, depth, True)

    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'min_max')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
