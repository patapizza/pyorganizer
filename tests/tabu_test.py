#!/usr/bin/env python3

import unittest
from organizer import *

class TabuTest(unittest.TestCase):

    def setUp(self):
        self.p = [[1, 1, 1, 1], [1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 1], [0, 1, 0, 1], [0, 1, 0, 1]]
        self.p_ = [[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.c = [2, 6, 1, 4]
        self.d = [[1, 1, 0, 1], [1, 1, 0, 1], [0, 0, 1, 0], [1, 1, 0, 1]]
        self.o = Organizer(self.p, self.c, self.d)

    def test_fitness_max(self):
        self.assertEqual(13, self.o.fitness_max(self.p), "wrong fitness score for p")
        self.assertEqual(2, self.o.fitness_max(self.p_), "wrong fitness score for p_")
        self.assertEqual(10, self.o.fitness_max(self.d), "wrong fitness score for d")

    def test_fitness_mean(self):
        p = [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
        self.assertEqual(0.0, self.o.fitness_mean(p), "wrong fitness_mean score")
        p = [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 0, 1]]
        self.assertEqual(0.16666666666666666, self.o.fitness_mean(p), "wrong fitness_mean score")

    def test_make_consistent(self):
        self.assertEqual(self.p_, self.o.make_consistent(), "inconsistent basic solution")

    def test_neighborhood(self):
        n = [[[1, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[0, 1, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[0, 0, 1, 1], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
             [[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
             [[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]],
             [[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 1, 0, 0]],
             [[0, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]]]
        i = 0
        for s in self.o.neighborhood(self.p_):
            self.assertEqual(n[i], s, "neighbor #%d is different than expected" % i)
            i += 1

    def test_tabu(self):
        s0 = [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
        self.assertEqual(s0, self.o.tabu(), "solution is different than expected")
        self.o.set_capacity([2, 0, 1, 4])
        self.assertEqual(s0, self.o.tabu(), "solution is different than expected")
        s1 = [[1, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 0, 1]]
        self.o.set_capacity([2, 2, 1, 4])
        self.assertEqual(s1, self.o.tabu(), "solution is different than expected")

if __name__ == '__main__':
    unittest.main()
