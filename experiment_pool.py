import io
import os
import threading
import time
from contextlib import redirect_stdout
from itertools import product
from multiprocessing import Pool, Lock
from os.path import join as joinPath

from matplotlib import pyplot as plt

import run_game

RESULTS_DIR = 'results_' + time.strftime("%m%d_%H%M")
RESULTS_DIR = 'results_1226_1531'

TEMP_DIR = joinPath(RESULTS_DIR, 'temp')
FINAL_CSV = joinPath(RESULTS_DIR, 'final.csv')
FINAL_TABLE_CSV = joinPath(RESULTS_DIR, 'final_table.csv')

players = ['simple_player', 'alpha_beta_player', 'min_max_player', 'better_player']
times = ['2', '10', '50']
NUM_OF_GAMES = 5

MAX_CONCURENCY = 3
file_lock = Lock()

def getfilename(p1, p2, t):
    return joinPath(TEMP_DIR, '{}.{}.{}.txt'.format(p1, p2, t))


def callto(p1, p2, t):
    print('python3 run_game.py 2 {} 5 n {} {}'.format(t, p1, p2))

    with io.StringIO() as f, redirect_stdout(f):
        run_game.GameRunner(2, t, 5, 'n', p1, p2).run()
        s = f.getvalue()

    filename = getfilename(p1, p2, t)

    file_lock.acquire()
    with open(filename, "a") as f:
        f.write(s)
    file_lock.release()


def run_threads():

    with Pool(processes=MAX_CONCURENCY) as pool:
        pool.starmap(
            callto,
            map(lambda x: x[:-1], # prepare 'callto' arguments
                filter(lambda x: x[0] != x[1], # only different players
                       product(players, players, times, range(NUM_OF_GAMES)))),
            chunksize=2
        )


def create_final_result_and_csv_file():
    final_result = {player: {t: 0 for t in times} for player in players}
    final = open(FINAL_CSV, 'w')
    for p1, p2, time in product(players, players, times):
        if p1 == p2:
            continue
        file_name = getfilename(p1, p2, time)
        with open(file_name, 'r') as file:
            for line in file.readlines():
                print('line is:{}'.format(line))
                winner = 'The winner is' in line
                exceeded = 'exceeded resources' in line
                is_p1 = p1[:-len('_player')] in line

                p1_score = '0.5'
                p2_score = '0.5'
                if winner:
                    if is_p1:
                        p1_score = '1'
                        p2_score = '0'
                    else:
                        p1_score = '0'
                        p2_score = '1'
                elif exceeded:
                    if is_p1:
                        p1_score = '0'
                        p2_score = '1'
                    else:
                        p1_score = '1'
                        p2_score = '0'

                final_result[p1][time] += float(p1_score)
                final_result[p2][time] += float(p2_score)
                line_to_print = p1 + ',' + p2 + ',' + time + ',' + p1_score + ',' + p2_score + '\n'
                final.write(line_to_print)

    final.close()
    return final_result


def create_graph_and_final_table(final_result):
    final_table = open(FINAL_TABLE_CSV, 'w')
    headers = 't = 2, t = 10, t = 50, player_name\n'
    final_table.write(headers)
    plt.figure()
    x = [int(t) for t in times]
    plt.title('Scores as a function of t')
    for player in players:
        time_to_point = final_result[player]
        y = [time_to_point[t] for t in times]
        line = ','.join(map(str, y))
        line += ',' + player + '\n'
        final_table.write(line)
        plt.plot(x, y, '.-', label=player)
    final_table.close()
    plt.legend()
    plt.show()


def main():
    if os.path.isdir(RESULTS_DIR):
        print("~"*15)
        print("Found already existing directory! just displayin summarize")
        print("~"*15)
    else:
        os.mkdir(RESULTS_DIR)
        os.mkdir(TEMP_DIR)
        run_threads()
    final_result = create_final_result_and_csv_file()
    create_graph_and_final_table(final_result)


if __name__ == '__main__':
    main()
