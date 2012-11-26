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

    def test_initial_solution_bu(self):
        print("Initial solution (bottom up): {}".format(initial_solution_bottom_up(self.p, self.c, self.d)))

    def test_initial_solution_td(self):
        print("Initial solution (top down): {}".format(initial_solution_top_down(self.p, self.c, self.d)))
    
    @unittest.skip("just testing initial solutions for now")
    def test_tabu(self):
        print("Best solution found: {}".format(tabu_search([[0 for pp in p] for p in self.p])))

if __name__ == '__main__':
    unittest.main()
