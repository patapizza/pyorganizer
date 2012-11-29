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
        self.c = [random.randint(0, n + 1) for i in range(m)]
        '''generating the preferences' matrix'''
        self.p = [[random.randint(0, 1) for i in range(m)] for j in range(n)]
        '''generating the exclusion matrix'''
        '''TODO: d = d^T'''
        self.d = [[random.randint(0, 1) for i in range(m)] for j in range(m)]
        '''TODO: emin, emax, friends'''
