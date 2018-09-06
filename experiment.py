import os
import io
import re
import shutil
import threading
import time
from os.path import join as joinPath
from subprocess import Popen, PIPE
from itertools import product
from sys import executable as PythonExec

from matplotlib import pyplot as plt

RESULTS_DIR = 'results_' + time.strftime("%m%d_%H%M")

TEMP_DIR = joinPath(RESULTS_DIR, 'temp')
FINAL_CSV = joinPath(RESULTS_DIR, 'final.csv')
FINAL_TABLE_CSV = joinPath(RESULTS_DIR, 'final_table.csv')

MAX_CONCURENCY = 4
global_sema = threading.Semaphore(value=MAX_CONCURENCY)
file_sema = threading.Semaphore(value=1)
players = ['simple_player', 'better_player', 'alpha_beta_player', 'min_max_player']
times = ['2', '10', '50']
NUM_OF_GAMES = 5


def getfilename(p1, p2, time):
    return joinPath(TEMP_DIR, '{}.{}.{}.txt'.format(p1, p2, time))


def callto(time, p1, p2):
    global_sema.acquire()
    file_name = getfilename(p1, p2, time)

    print('python3 run_game.py 2 {} 5 n {} {}'.format(time, p1, p2))
    p = Popen([PythonExec, 'run_game.py', '2', time, '5', 'n', p1, p2], stdout=PIPE)
    outs, errs = p.communicate()
    global_sema.release()

    file_sema.acquire()
    with open(file_name, 'a') as file:
        file.write(outs.decode())
    file_sema.release()


def run_threads():
    threads = []

    for p1 in players:
        for p2 in players:
            if p1 == p2:
                continue
            for time in times:
                for _ in range(NUM_OF_GAMES):
                    t = threading.Thread(target=callto, args=[time, p1, p2])
                    threads.append(t)
                    t.start()

    for t in threads:
        t.join()


def create_final_result_and_csv_file():
    final_result = {player: {t: 0 for t in times} for player in players}
    final = open(FINAL_CSV, 'w')
    for p1 in players:
        for p2 in players:
            if p1 == p2:
                continue
            for time in times:
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
        line = ''
        for point in y:
            line += str(point) + ','
        line += player + '\n'
        final_table.write(line)
        plt.plot(x, y, '.-', label=player)
    final_table.close()
    plt.legend()
    plt.show()


def main():
    os.mkdir(RESULTS_DIR)
    os.mkdir(TEMP_DIR)
    run_threads()
    final_result = create_final_result_and_csv_file()
    create_graph_and_final_table(final_result)


if __name__ == '__main__':
    main()
