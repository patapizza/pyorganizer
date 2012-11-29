#!/usr/bin/env python3

import time
import unittest
from generator import *
from tabu_search import *

class TSTest(unittest.TestCase):

    @unittest.skip("using generator")
    def test_large_problem(self):
        p = [[1] * 100] * 100
        c = [i for i in range(100)]
        d = []
        for i in range(100):
            row = []
            for j in range(100):
                if i % 2 != 0:
                    if j % 2 == 0:
                        row.append(1)
                    else:
                        row.append(0)
                else:
                    if j % 2 == 0:
                        row.append(0)
                    else:
                        row.append(1)
            d.append(row)
        print(d)
        status = Status(p, c, d, 10)
        status.set_status()
        print("Huge solution found: {}".format(tabu_search(initial_solution_top_down(p, c, d))))
        #print("Huge solution found: {}".format(tabu_search([[0] * 100 for s in p])))

    def test_generator(self):
        n = 50 # number of participants
        m = 20 # number of events
        gen = Generator(n, m)
        print("Testing instance n: {} m: {}".format(n, m))
        td = initial_solution_top_down(gen.p, gen.c, gen.d)
        bu = initial_solution_bottom_up(gen.p, gen.c, gen.d)
        attempts = [3, 10, 20, 50, 100]
        attempts = [100]
        tenures = [2, 4]
        for attempt in attempts:
            print("# attempts: {}".format(attempt))
            for tenure in tenures:
                print("Tenure value: {}".format(tenure))
                status = Status(gen.p, gen.c, gen.d, attempt, tenure)
                status.set_status()
                start = time.time()
                print("Solution found from 0-matrix initial solution: {}".format(tabu_search([[0] * m for i in range(n)])[1]))
                print("Elapsed: {}".format(time.time() - start))
                status = Status(gen.p, gen.c, gen.d, attempt, tenure)
                status.set_status()
                start = time.time()
                print("Solution found from top-down initial solution: {}".format(tabu_search(td)[1]))
                print("Elapsed: {}".format(time.time() - start))
                status = Status(gen.p, gen.c, gen.d, attempt, tenure)
                status.set_status()
                start = time.time()
                print("Solution found from bottom-up initial solution: {}".format(tabu_search(bu)[1]))
                print("Elapsed: {}".format(time.time() - start))

    @unittest.skip("all is alright")
    def test_tiny(self):
        p = [[1, 1, 1, 1], [1, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 1], [0, 1, 0, 1]]
        c = [2, 6, 1, 4]
        d = [[1, 1, 0, 1], [1, 1, 0, 1], [0, 0, 1, 0], [1, 1, 0, 1]]
        status = Status(p, c, d)
        status.set_status()
        print(tabu_search(initial_solution_bottom_up(p, c, d)))

if __name__ == '__main__':
    unittest.main()
