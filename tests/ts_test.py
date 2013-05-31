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

import time
import unittest
from generator import *
from tabu_search import *

class TSTest(unittest.TestCase):

    @unittest.skip("")
    def test_initial_solution(self):
        n = 50
        m = 100
        loops = 100
        bu = 0
        td = 0
        while loops:
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
            status.set_status()
            init_bu = initial_solution_bottom_up(gen.p, gen.c, gen.d)
            init_td = initial_solution_top_down(gen.p, gen.c, gen.d)
            score_bu = objective_compound(init_bu).total
            score_td = objective_compound(init_td).total
            score_zero = objective_compound([[0] * m for i in range(n)]).total
            print("bu: {} :: td: {} :: zero: {}".format(score_bu, score_td, score_zero))
            bu += score_bu
            td += score_td
            loops -= 1
        print("bu: {} td: {}".format(bu / 100, td / 100))

    @unittest.skip("To run this test, you need to return the number of iterations within tabu_search")
    def test_tabu_search(self):
        n = 50
        m = 100
        loops = 30
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
        status.allowed_time = 300
        status.improving = 1
        status.delta = 1
        status.restarts = 20
        status.attempts = 100000
        status.set_status()
        init = initial_solution_bottom_up(gen.p, gen.c, gen.d)
        results = {}
        tenures = [0, 2, 5, 10]
        legal = [is_legal_not_tabu, is_legal_not_tabu_aspiration]
        for i in range(loops):
            for tenure in tenures:
                status.tenure = tenure
                print("Tenure value: {}".format(tenure))
                for aspiration in legal:
                    print("Legal function: {}".format(aspiration))
                    start = time.time()
                    a, s, score = tabu_search(init, objective_compound_incr, neighborhood_all, aspiration, selection_first_improvement)
                    elapsed = time.time() - start
                    print("Solution (first improvement): {} in {} sec ({} attempts)".format(score, elapsed, a))
                    status.k = 3
                    start = time.time()
                    a_, s_, score_ = tabu_search(init, objective_compound_incr, neighborhood_all, aspiration, selection_best_k)
                    elapsed_ = time.time() - start
                    print("Solution (best 3): {} in {} sec ({} attempts)".format(score_, elapsed_, a_))
                    status.k = 5
                    start = time.time()
                    a__, s__, score__ = tabu_search(init, objective_compound_incr, neighborhood_all, aspiration, selection_best_k)
                    elapsed__ = time.time() - start
                    print("Solution (best 5): {} in {} sec ({} attempts)".format(score__, elapsed__, a__))
                    if i == 0:
                        results[(tenure, aspiration.__name__, "first_improvement")] = [(score, elapsed, a)]
                        results[(tenure, aspiration.__name__, "best_3")] = [(score_, elapsed_, a_)]
                        results[(tenure, aspiration.__name__, "best_5")] = [(score__, elapsed__, a__)]
                    else:
                        results[(tenure, aspiration.__name__, "first_improvement")].append((score, elapsed, a))
                        results[(tenure, aspiration.__name__, "best_3")].append((score_, elapsed_, a_))
                        results[(tenure, aspiration.__name__, "best_5")].append((score__, elapsed__, a__))
        for k, v in sorted(results.items()):
            score_all, elapsed_all, a_all = 0, 0, 0
            for score, elapsed, a in v:
                score_all += score
                elapsed_all += elapsed
                a_all += a
            print("{} -> {:.4f} in {:.2f} sec, {} attempts (average on {} iterations)".format(k, score_all / loops, elapsed_all / loops, a_all / loops, loops))

    @unittest.skip("To run this test, you need to return the number of iterations within tabu_search_restarts and tabu_search")
    def test_tabu_restarts(self):
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
        status.allowed_time = 300
        status.attempts = 100000
        status.restarts = 100000
        status.k = 3
        status.set_status()
        results = {}
        improving = [1, 3, 5]
        delta = [1, 5, 10]
        for i in range(loops):
            for improving_ in improving:
                print("Improving: {}".format(improving_))
                status.improving = improving_
                for delta_ in delta:
                    print("Delta: {}".format(delta_))
                    status.delta = delta_
                    status.tenure = 5
                    start = time.time()
                    a, s, score = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, is_legal_not_tabu_aspiration, selection_best_k)
                    elapsed = time.time() - start
                    print("Score (tenure=5, aspiration): {:.4f} in {:.2f} sec ({} attempts)".format(score, elapsed, a))
                    if i == 0:
                        results[(improving_, delta_, 5, "aspiration")] = [(score, elapsed, a)]
                    else:
                        results[(improving_, delta_, 5, "aspiration")].append((score, elapsed, a))
                    status.tenure = 10
                    start = time.time()
                    a, s, score = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, is_legal_not_tabu_aspiration, selection_best_k)
                    elapsed = time.time() - start
                    print("Score (tenure=10, aspiration): {:.4f} in {:.2f} sec ({} attempts)".format(score, elapsed, a))
                    if i == 0:
                        results[(improving_, delta_, 10, "aspiration")] = [(score, elapsed, a)]
                    else:
                        results[(improving_, delta_, 10, "aspiration")].append((score, elapsed, a))
                    status.tenure = 0
                    start = time.time()
                    a, s, score = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, is_legal_not_tabu, selection_best_k)
                    elapsed = time.time() - start
                    print("Score (tenure=0, no aspiration): {:.4f} in {:.2f} sec ({} attempts)".format(score, elapsed, a))
                    if i == 0:
                        results[(improving_, delta_, 0, "no aspiration")] = [(score, elapsed, a)]
                    else:
                        results[(improving_, delta_, 0, "no aspiration")].append((score, elapsed, a))
                    status.tenure = 2
                    start = time.time()
                    a, s, score = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, is_legal_not_tabu_aspiration, selection_best_k)
                    elapsed = time.time() - start
                    print("Score (tenure=2, aspiration): {:.4f} in {:.2f} sec ({} attempts)".format(score, elapsed, a))
                    if i == 0:
                        results[(improving_, delta_, 2, "aspiration")] = [(score, elapsed, a)]
                    else:
                        results[(improving_, delta_, 2, "aspiration")].append((score, elapsed, a))
                    status.tenure = 2
                    start = time.time()
                    a, s, score = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, is_legal_not_tabu, selection_best_k)
                    elapsed = time.time() - start
                    print("Score (tenure=2, no aspiration): {:.4f} in {:.2f} sec ({} attempts)".format(score, elapsed, a))
                    if i == 0:
                        results[(improving_, delta_, 2, "no aspiration")] = [(score, elapsed, a)]
                    else:
                        results[(improving_, delta_, 2, "no aspiration")].append((score, elapsed, a))
        for k, v in sorted(results.items()):
            score_all, elapsed_all, attempts_all = 0, 0, 0
            for score, elapsed, a in v:
                score_all += score
                elapsed_all += elapsed
                attempts_all += a
            print("{} -> {:.4f} in {:.2f} sec, {:.2f} attempts (average on {} iterations)".format(k, score_all / loops, elapsed_all / loops, attempts_all / loops, loops))

    @unittest.skip("To run this test, you need to return the number of iterations within tabu_search and tabu_search_restarts")
    def test_tabu_vs_restarts(self):
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
        status.allowed_time = 3600
        status.restarts = 20
        status.k = 3
        status.attempts = 10000
        status.set_status()
        init = initial_solution_bottom_up(gen.p, gen.c, gen.d)
        results = {}
        for i in range(loops):
            status.improving = 5
            status.delta = 1
            status.tenure = 2
            start = time.time()
            a, s, score = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, is_legal_not_tabu, selection_best_k)
            elapsed = time.time() - start
            if i == 0:
                results[("restarts", "stagn=5", "no aspiration")] = [(a, score, elapsed)]
            else:
                results[("restarts", "stagn=5", "no aspiration")].append((a, score, elapsed))
            print("Score restarts (tenure=5): {:.4f} in {:.2f} sec ({:.2f} iterations)".format(score, elapsed, a))
            status.tenure = 5
            start = time.time()
            a, s, score = tabu_search(init, objective_compound_incr, neighborhood_all, is_legal_not_tabu_aspiration, selection_best_k, 0)
            elapsed = time.time() - start
            if i == 0:
                results[("tabu", 5, "aspiration")] = [(a, score, elapsed)]
            else:
                results[("tabu", 5, "aspiration")].append((a, score, elapsed))
            print("Score tabu (tenure=5, aspiration): {:.4f} in {:.2f} sec ({:.2f} iterations)".format(score, elapsed, a))
            status.tenure = 0
            start = time.time()
            a, s, score = tabu_search(init, objective_compound_incr, neighborhood_all, is_legal_not_tabu, selection_best_k, 0)
            elapsed = time.time() - start
            if i == 0:
                results[("tabu", 0, "no aspiration")] = [(a, score, elapsed)]
            else:
                results[("tabu", 0, "no aspiration")].append((a, score, elapsed))
            print("Score tabu (tenure=0, no aspiration): {:.4f} in {:.2f} sec ({:.2f} iterations)".format(score, elapsed, a))
            status.tenure = 2
            status.improving = 1
            start = time.time()
            a, s, score = tabu_search_restarts(initial_solution_bottom_up, objective_compound_incr, neighborhood_all, is_legal_not_tabu_aspiration, selection_best_k)
            elapsed = time.time() - start
            if i == 0:
                results[("restarts", "stagn=1", "aspiration")] = [(a, score, elapsed)]
            else:
                results[("restarts", "stagn=1", "aspiration")].append((a, score, elapsed))
            print("Score restarts (tenure=10): {:.4f} in {:.2f} sec ({:.2f} iterations)".format(score, elapsed, a))
        for k, v in sorted(results.items()):
            score_all, elapsed_all, attempts_all = 0, 0, 0
            for a, score, elapsed in v:
                score_all += score
                elapsed_all += elapsed
                attempts_all += a
            print("{} -> {:.4f} in {:.2f} sec, {:.2f} attempts (average on {} iterations)".format(k, score_all / loops, elapsed_all / loops, attempts_all / loops, loops))

if __name__ == '__main__':
    unittest.main()
