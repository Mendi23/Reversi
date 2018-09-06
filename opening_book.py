
import re
import collections
import string
from itertools import chain
from Reversi.consts import *

CORPUS_SIZE = 70
NUM_OF_MOVES = 10


class MovesDict:

    def __init__ (self, path='book.gam'):

        self.move_series = [(3,3),(3,4),(4,4),(4,3)]
        words = re.findall(r'^(?:[+\-][a-z][0-9]){%d}' % NUM_OF_MOVES,
                           open(path).read().lower(),re.MULTILINE)

        tempDict = {ord(a):ord(n) for a,n in\
                    chain(zip(string.ascii_letters[:9], string.digits[:9]),
                          zip(string.digits[1:], string.digits[:9]))}

        openingBook = []
        for line in collections.Counter(words).most_common(CORPUS_SIZE):
            pairs = re.findall(r"[+\-](\d)(\d)", line[0].translate(tempDict))
            openingBook.append([(BOARD_COLS-1-int(pair[0]), int(pair[1])) for pair in pairs])

        openingBook.reverse()
        self.openingDict = {}
        for opening in openingBook:
            for i in range(NUM_OF_MOVES):
                self.openingDict[tuple(self.move_series + opening[0:i])] = opening[i]


    def update_moves_series(self, board, newMove = None):
        if (newMove):
            self.move_series.append(tuple(newMove))
            return

        for i in range (BOARD_COLS):
            for j in range (BOARD_ROWS):
                if (board[i][j] != EM and (i,j) not in self.move_series):
                    self.move_series.append((i,j))
                    return

    def get_new_move(self):
        return self.openingDict.get(tuple(self.move_series))
