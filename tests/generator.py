#!/usr/bin/env python3

import random

class Generator:

    '''
        input:
            _n: the number of participants
            _m: the number of events
    '''
    def __init__(self, n, m):
        '''generating the capacity vector'''
        self.c = [random.randint(0, n) for i in range(m)]
        '''generating the preferences' matrix'''
        self.p = [[random.uniform(0, 2) for i in range(m)] for j in range(n)]
        '''generating the exclusion matrix'''
        self.d = [[0 for i in range(m)] for j in range(m)]
        for i in range(m):
            for j in range(m):
                if i == j:
                    self.d[i][j] = 1
                else:
                    v = random.randint(0, 1)
                    self.d[i][j] = v
                    self.d[j][i] = v
        '''generating close friends graph'''
        self.cf = [[random.randint(0, 1) for i in range(n)] for j in range(n)]
        '''generating emin vector, and chosen_ones'''
        self.emin = []
        self.chosen_ones = {}
        for i in range(n):
            x = 0
            for j in range(m):
                if self.p[i][j] >= 1:
                    x += 1
                    if random.randint(0, 1) == 0:
                        self.chosen_ones[(i, j)] = 1
            self.emin.append(random.randint(0, x))
        '''generating emax vector'''
        self.emax = [random.randint(self.emin[i], m) for i in range(n)]
        '''generating mage vector'''
        self.mage = [random.randint(20, 25) for i in range(m)]
        '''generating age vector'''
        self.age = [random.randint(16, 25) for i in range(n)]
        '''generating male vector'''
        self.male = [random.randint(0, 1) for i in range(n)]
        '''generating sratio vector'''
        self.sratio = [random.uniform(0, 1) for i in range(m)]
        '''generating cmin vector'''
        self.cmin = [random.randint(0, self.c[j]) for j in range(m)]
