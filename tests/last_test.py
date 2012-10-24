#!/usr/bin/env python3

import unittest
from last import *

class LastTest(unittest.TestCase):

    def setUp(self):
        self.p = [[1, 1, 1, 1], [1, 1, 0, 0], [1, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 1], [0, 1, 0, 1]]
        self.c = [2, 6, 1, 4]
        self.d = [[1, 1, 0, 1], [1, 1, 0, 1], [0, 0, 1, 0], [1, 1, 0, 1]]
        self.o = Organizer(self.p, self.c, self.d)

    def test_make_consistent(self):
        print(self.o.make_consistent())
        print(self.o.tabu())

if __name__ == '__main__':
    unittest.main()
