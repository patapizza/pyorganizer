#!/usr/bin/env python3

# Copyright 2012, 2013 Yves Deville, Jean-Baptiste Mairy, Julien Odent
#
# This file is part of pyorganizer.
#
# pyorganizer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyorganizer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyorganizer.  If not, see <http://www.gnu.org/licenses/>.

import random

class Generator:

    '''
        input:
            _n: the number of participants
            _m: the number of events
    '''
    def __init__(self, n, m):
        '''
            Hard constraints
        '''
        '''generating the capacity vector'''
        self.c = [random.randint(0, n) for i in range(m)]
        '''generating the preferences' matrix'''
        self.p = []
        p_values = []
        row_capacity = [0] * n
        col_capacity = [0] * m
        s = [[0] * m for i in range(n)]
        s_indices = []
        for i in range(n):
            p = []
            s_indices.append([])
            for j in range(m):
                r = random.uniform(0, 2)
                p.append(r)
                if r >= 1:
                    p_values.append((i, j))
            self.p.append(p)
        '''generating the exclusion matrix'''
        self.d = [[0 for i in range(m)] for j in range(m)]
        d_indices = []
        for i in range(m):
            dd = []
            for j in range(m):
                if i == j:
                    self.d[i][j] = 1
                else:
                    v = random.randint(0, 1)
                    self.d[i][j] = v
                    self.d[j][i] = v
                    if v == 1:
                        dd.append(j)
            d_indices.append(dd)
        '''generating close friends graph'''
        self.cf = [[random.randint(0, 1) for i in range(n)] for j in range(n)]
        '''generating emin vector (soft constraint, needed now for emax computation)'''
        self.emin = []
        for i in range(n):
            x = 0
            for j in range(m):
                if self.p[i][j] >= 1:
                    x += 1
            self.emin.append(random.randint(0, x))
        '''generating emax vector'''
        self.emax = [random.randint(self.emin[i], m) for i in range(n)]
        '''generating chosen_ones'''
        self.chosen_ones = {}
        while len(p_values) > 0:
            i, j = p_values[random.randint(0, len(p_values) - 1)]
            p_values.remove((i, j))
            if row_capacity[i] == self.emax[i] or (self.c[j] != 0 and col_capacity[j] == self.c[j]):
                continue
            if len(set(s_indices[i]) & set(d_indices[j])) == 0:
                s[i][j] = 1
                row_capacity[i] += 1
                col_capacity[j] += 1
                s_indices[i].append(j)
                if random.randint(0, 1) == 0:
                    self.chosen_ones[(i, j)] = 1

        '''
            Soft constraints
        '''
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
