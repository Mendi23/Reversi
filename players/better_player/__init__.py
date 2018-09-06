import abstract
from utils import INFINITY, run_with_limited_time, ExceededTimeError
from Reversi.consts import EM, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS
import time
import copy
from opening_book import MovesDict
from opening_book import NUM_OF_MOVES

w1 = 0.3
w2 = 0.3
w3 = 0.4


class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.time()
        self.gameCorpus = MovesDict()
        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

    def get_move(self, game_state, possible_moves):
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

        best_move = self.get_move_logic(game_state, possible_moves)

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        return best_move

    def get_move_logic(self, game_state, possible_moves):
        self.gameCorpus.update_moves_series(game_state.board)
        best_move = possible_moves[0]

        if len(possible_moves) != 1:
            t = self.opening_move()
            if (t):
                best_move = t
            else:
                next_state = copy.deepcopy(game_state)
                next_state.perform_move(best_move[0], best_move[1])
                # Choosing an arbitrary move
                # Get the best move according the utility function

                for move in possible_moves:
                    new_state = copy.deepcopy(game_state)
                    new_state.perform_move(move[0], move[1])
                    if self.utility(new_state) > self.utility(next_state):
                        next_state = new_state
                        best_move = move

        self.gameCorpus.update_moves_series(game_state.board, best_move)
        return best_move

    def utility(self, state):
        valid_moves = state.get_possible_moves()
        if len(valid_moves) == 0:
            winner = state.get_winner()
            if winner == self.color:
                return INFINITY
            elif winner == OPPONENT_COLOR[self.color]:
                return -INFINITY
            else:
                return 0

        h_coins = self.getCoins(state)
        h_moves = self.getMoves(state, valid_moves)
        h_stables = self.getAdjacentToCorner(state)

        return w1 * h_coins + w2 * h_moves + w3 * h_stables

    def calc(self, my, other):
        if (my + other) == 0:
            return 0
        return 100 * (my - other) / (my + other)

    def getCoins(self, state):
        my_u = 0
        op_u = 0
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if state.board[x][y] == self.color:
                    my_u += 1
                if state.board[x][y] == OPPONENT_COLOR[self.color]:
                    op_u += 1

        return 100 * (my_u - op_u) / (BOARD_COLS * BOARD_ROWS)

    def getMoves(self, state, valid_moves):
        original_player = state.curr_player
        state.curr_player = OPPONENT_COLOR[state.curr_player]
        other_moves = state.get_possible_moves()
        state.curr_player = original_player

        return \
            self.calc(len(valid_moves), len(other_moves)) if state.curr_player == self.color \
                else self.calc(len(other_moves), len(valid_moves))

    def getAdjacentToCorner(self, state):
        corners = ((0, 0), (BOARD_COLS - 1, 0), (0, BOARD_ROWS - 1),
                   (BOARD_COLS - 1, BOARD_ROWS - 1))

        plPoints = set()
        opPoints = set()

        for c in corners:
            currCornerColor = state.board[c[0]][c[1]]
            if (currCornerColor == self.color):
                toAdd = plPoints
            elif (currCornerColor == OPPONENT_COLOR[self.color]):
                toAdd = opPoints
            else:
                continue

            directions = (
                (-1, 0),
                (0, -1),
                (1, 0),
                (0, 1)
            )

            for d in directions:
                x, y = c[0], c[1]
                while (state.isOnBoard(x, y) and state.board[x][y] == currCornerColor):
                    toAdd.add((x, y))
                    x += d[0]
                    y += d[1]

        return self.calc(len(plPoints), len(opPoints))

    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def opening_move(self):
        return self.gameCorpus.get_new_move()

    def no_more_time(self):
        return (time.time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
