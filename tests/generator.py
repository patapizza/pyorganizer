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
        # todo: preferences ordering between 0 and 2
        self.p = [[random.randint(0, 1) for i in range(m)] for j in range(n)]
        '''generating the exclusion matrix'''
        '''TODO: d = d^T'''
        self.d = [[random.randint(0, 1) for i in range(m)] for j in range(m)]
        '''TODO: emin, emax, friends'''
        '''generating close friends graph'''
        self.cf = [[random.randint(0, 1) for i in range(n)] for j in range(n)]
        '''generating emin vector'''
        self.emin = [random.randint(0, sum(i for i in self.p[j])) for j in range(n)]
        '''generating mage vector'''
        self.mage = [random.randint(0, 50) for i in range(m)]
        '''generating age vector'''
        self.age = [random.randint(0, 50) for i in range(n)]
