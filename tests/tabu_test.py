#!/usr/bin/env python3

import unittest
from tabu import *

class TabuTest(unittest.TestCase):

    def setUp(self):
        self.p = [[1, 1, 1, 1], [1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 1], [0, 1, 0, 1], [0, 1, 0, 1]]
        self.p_ = [[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        # self.s0 = [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
        self.c = [2, 6, 1, 4]
        self.d = [[1, 1, 0, 1], [1, 1, 0, 1], [0, 0, 1, 0], [1, 1, 0, 1]]

    def test_fitness(self):
        self.assertEqual(13, fitness(self.p), "wrong fitness score for p")
        self.assertEqual(2, fitness(self.p_), "wrong fitness score for p_")
        self.assertEqual(10, fitness(self.d), "wrong fitness score for d")

    def test_make_consistent(self):
        self.assertEqual(self.p_, make_consistent(self.p, self.c, self.d), "inconsistent basic solution")

    # def test_initial_solution(self):
        # self.assertEquals(self.s0, make_initial_solution(self.p_))

    def test_neighborhood(self):
        n = [[[1, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
             [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]]
        i = 0
        for s in neighborhood(self.p_, self.p, self.c, self.d):
            self.assertEqual(n[i], s, "neighbor #%d is different than expected" % i)
            i += 1

if __name__ == '__main__':
    unittest.main()
