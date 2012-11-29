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
        status = Status(p, c, d, 10)
        status.set_status()
        print("Huge solution found: {}".format(tabu_search(initial_solution_top_down(p, c, d))))

    @unittest.skip("blah")
    def test_generator(self):
        n = 50 # number of participants
        m = 20 # number of events
        gen = Generator(n, m)
        print("Testing instance n: {} m: {}".format(n, m))
        td = initial_solution_top_down(gen.p, gen.c, gen.d)
        bu = initial_solution_bottom_up(gen.p, gen.c, gen.d)
        attempts = [3, 10, 20, 50, 100]
        tenures = [2, 4]
        for attempt in attempts:
            print("{} attempts".format(attempt))
            for tenure in tenures:
                print("Tenure value: {}".format(tenure))
                status = Status(gen.p, gen.c, gen.d, attempt, tenure)
                status.set_status()
                start = time.time()
                print("Solution found from 0-matrix initial solution: {} in {} sec".format(tabu_search([[0] * m for i in range(n)])[1], time.time() - start))
                status.attempts = attempt
                start = time.time()
                print("Solution found from top-down initial solution: {} in {} sec".format(tabu_search(td)[1], time.time() - start))
                status.attempts = attempt
                start = time.time()
                print("Solution found from bottom-up initial solution: {} in {} sec".format(tabu_search(bu)[1], time.time() - start))

    @unittest.skip("all is alright")
    def test_tiny(self):
        p = [[1, 1, 1, 1], [1, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 1], [0, 1, 0, 1]]
        c = [2, 6, 1, 4]
        d = [[1, 1, 0, 1], [1, 1, 0, 1], [0, 0, 1, 0], [1, 1, 0, 1]]
        status = Status(p, c, d)
        status.set_status()
        print(tabu_search(initial_solution_top_down(p, c, d), objective_max_incr))

    def test_friends(self):
        status = Status([[0] * 3 for i in range(5)], [0] * 3, [[0] * 3 for i in range(3)])
        status.set_cf([[1, 0, 1, 1, 0], [0, 1, 1, 0, 0], [0, 0, 1, 1, 1], [1, 0, 1, 0, 1], [1, 1, 1, 1, 1]])
        status.set_status()
        self.assertEqual(5, objective_friends([[1, 0, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 0]]))
        self.assertEqual(6, objective_friends([[0, 0, 1], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 0]]))
        self.assertEqual(6, objective_friends([[0, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [0, 1, 0]]))
        self.assertEqual(6, objective_friends_incr([[1, 0, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 0]], 5, ('swap', (0, 2, 0, 2))))
        self.assertEqual(1, objective_friends([[1, 1, 0], [0, 0, 1], [1, 0, 0], [0, 0, 1], [0, 0, 0]]))
        self.assertEqual(1, objective_friends_incr([[1, 1, 0], [0, 0, 1], [1, 0, 0], [0, 0, 1], [0, 0, 0]], 1, ('swap', (0, 3, 1, 2))))

    #@unittest.skip("blah")
    def test_aspiration(self):
        n = 50
        m = 20
        gen = Generator(n, m)
        init = initial_solution_top_down(gen.p, gen.c, gen.d)
        attempts = [3, 10, 20, 50]
        tenures = [2, 4]
        for attempt in attempts:
            print("{} attempts".format(attempt))
            for tenure in tenures:
                print("Tenure value: {}".format(tenure))
                status = Status(gen.p, gen.c, gen.d, attempt, tenure)
                status.set_cf(gen.cf)
                status.set_status()
                start = time.time()
                s, score = tabu_search(init, objective_friends_incr)
                print("Solution found: {} in {} sec".format(score, time.time() - start))
                #status.attempts = attempt
                #start = time.time()
                #print("Solution found with aspiration: {} in {} sec".format(tabu_search(init, objective_compound_incr, neighborhood_all, is_legal_not_tabu_aspiration)[1], time.time() - start))

if __name__ == '__main__':
    unittest.main()
