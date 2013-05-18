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

    def test_init_fun(self):
        n = 6
        m = 4
        gen = Generator(n, m)
        status = Status(gen.p, gen.c, gen.d)
        status.set_emax(gen.emax)
        status.chosen_ones = gen.chosen_ones
        status.set_status()
        print("p: {}".format(gen.p))
        print("d: {}".format(gen.d))
        print("c: {}".format(gen.c))
        print("emax: {}".format(gen.emax))
        print("chosen_ones: {}".format(gen.chosen_ones))
        print("s_bottom_up: {}".format(initial_solution_bottom_up(gen.p, gen.c, gen.d)))
        print("s_top_down: {}".format(initial_solution_top_down(gen.p, gen.c, gen.d)))
        print("s_confirmed: {}".format(initial_solution_confirmed_only()))

    #@unittest.skip("later")
    def test_selection(self):
        n = 50
        m = 100
        loops = 1
        gen = Generator(n, m)
        status = Status(gen.p, gen.c, gen.d)
        status.set_cf(gen.cf)
        status.set_emin(gen.emin)
        status.set_emax(gen.emax)
        status.set_age(gen.age)
        status.set_mage(gen.mage)
        status.set_male(gen.male)
        status.set_sratio(gen.sratio)
        status.set_cmin(gen.cmin)
        #status.chosen_ones = gen.chosen_ones
        status.allowed_time = 3000
        status.improving = 1
        status.delta = 1
        status.restarts = 10
        status.set_status()
        init = initial_solution_bottom_up(gen.p, gen.c, gen.d)
        results = {}
        attempts = [10, 20, 50, 100]
        tenures = [0, 1, 2, 5]
        legal = [is_legal_not_tabu, is_legal_not_tabu_aspiration]
        for i in range(loops):
            for attempt in attempts:
                status.attempts = attempt
                print("{} attempts".format(attempt))
                for tenure in tenures:
                    status.tenure = tenure
                    print("Tenure value: {}".format(tenure))
                    for aspiration in legal:
                        print("Legal function: {}".format(aspiration))
                        start = time.time()
                        s, score = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, aspiration, selection_first_improvement)
                        elapsed = time.time() - start
                        print("Solution (first improvement): {} in {} sec".format(score, elapsed))
                        status.k = 3
                        start = time.time()
                        s_, score_ = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, aspiration, selection_best_k)
                        elapsed_ = time.time() - start
                        print("Solution (best 3): {} in {} sec".format(score_, elapsed_))
                        status.k = 5
                        start = time.time()
                        s__, score__ = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, aspiration, selection_best_k)
                        elapsed__ = time.time() - start
                        print("Solution (best 5): {} in {} sec".format(score__, elapsed__))
                        if i == 0:
                            results[(attempt, tenure, aspiration.__name__, "first_improvement")] = [(score, elapsed)]
                            results[(attempt, tenure, aspiration.__name__, "best_3")] = [(score_, elapsed_)]
                            results[(attempt, tenure, aspiration.__name__, "best_5")] = [(score__, elapsed__)]
                        else:
                            results[(attempt, tenure, aspiration.__name__, "first_improvement")].append((score, elapsed))
                            results[(attempt, tenure, aspiration.__name__, "best_3")].append((score_, elapsed_))
                            results[(attempt, tenure, aspiration.__name__, "best_5")].append((score__, elapsed__))
        for k, v in sorted(results.items()):
            score_all, elapsed_all = 0, 0
            for score, elapsed in v:
                score_all += score
                elapsed_all += elapsed
            print("{} -> {:.4f} in {:.2f} sec (average on {} iterations)".format(k, score_all / loops, elapsed_all / loops, loops))

if __name__ == '__main__':
    unittest.main()
