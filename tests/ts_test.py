#!/usr/bin/env python3

import unittest
from tabu_search import *

class TSTest(unittest.TestCase):

    def setUp(self):
        self.p = [[1, 1, 1, 1], [1, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 1], [0, 1, 0, 1]]
        self.c = [2, 6, 1, 4]
        self.d = [[1, 1, 0, 1], [1, 1, 0, 1], [0, 0, 1, 0], [1, 1, 0, 1]]
        self.status = Status(self.p, self.c, self.d)
        self.status.set_status()

    def test_tabu(self):
        print("Best solution found: {}".format(tabu_search([[0 for pp in p] for p in self.p])))

    def test_initial_solution_td(self):
        print("Initial solution: {}".format(initial_solution_top_down(self.p, self.c, self.d)))

if __name__ == '__main__':
    unittest.main()
