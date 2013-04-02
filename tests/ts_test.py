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

    @unittest.skip("whatever")
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

    def test_selection(self):
        n = 10
        m = 10
        gen = Generator(n, m)
        init = initial_solution_top_down(gen.p, gen.c, gen.d)
        results = {}
        loops = 50
        for i in range(loops):
            attempts = [10, 20, 50, 100]
            tenures = [1, 2, 5, 10]
            l_function = [is_legal_not_tabu, is_legal_not_tabu_aspiration]
            for attempt in attempts:
                print("{} attempts".format(attempt))
                for tenure in tenures:
                    print("Tenure value: {}".format(tenure))
                    for aspiration in l_function:
                        print("Legal function: {}".format(aspiration))
                        status = Status(gen.p, gen.c, gen.d, attempt, tenure)
                        status.improving = 5 # ?
                        status.delta = 50 # ?
                        status.set_cf(gen.cf)
                        status.set_emin(gen.emin)
                        status.set_age(gen.age)
                        status.set_mage(gen.mage)
                        status.set_status()
                        start = time.time()
                        s, score = tabu_search(init, objective_compound_incr, neighborhood_all, aspiration, selection_first_improvement)
                        elapsed = time.time() - start
                        print("Solution (first improvement): {} in {} sec".format(score, elapsed))
                        status.attempts = attempt
                        status.k = 3
                        start = time.time()
                        s_, score_ = tabu_search(init, objective_compound_incr, neighborhood_all, aspiration, selection_best_k)
                        elapsed_ = time.time() - start
                        print("Solution (best 3): {} in {} sec".format(score_, elapsed_))
                        status.attempts = attempt
                        start = time.time()
                        s__, score__ = tabu_search(init, objective_compound_incr, neighborhood_all, aspiration, selection_best_k)
                        elapsed__ = time.time() - start
                        print("Solution (best 5): {} in {} sec".format(score__, elapsed__))
                        if i == 0:
                            results[(attempt, tenure, aspiration, 0)] = [(score, elapsed)]
                            results[(attempt, tenure, aspiration, 1)] = [(score_, elapsed_)]
                            results[(attempt, tenure, aspiration, 2)] = [(score__, elapsed__)]
                        else:
                            results[(attempt, tenure, aspiration, 0)].append((score, elapsed))
                            results[(attempt, tenure, aspiration, 1)].append((score_, elapsed_))
                            results[(attempt, tenure, aspiration, 2)].append((score__, elapsed__))
        for item in sorted(results.items()):
            for k, v in item:
                score_all, elapsed_all = 0, 0
                for score, elapsed in v:
                    score_all += score
                    elapsed_all += elapsed
                print("{} -> {} in {} sec (average on {} iterations)".format(k, score_all / loops, elapsed_all / loops, loops))

if __name__ == '__main__':
    unittest.main()
