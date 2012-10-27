#!/usr/bin/env python3

class Organizer:

    def __init__(self, p, c, d, attemps = 100):
        self.p = p
        self.c = c
        self.d = d
        self.attemps = attemps # amount of times to iterate
        self.MAX_SIZE = len(p) / 2 # size of the tabu list
        self.emax = [] # max events that participants want to attend
        for x in range(len(p)):
            score = 0
            for y in range(len(p[0])):
                score += y
            self.emax.append(score)
        self.emin = [0 for x in range(len(p))] # min events that participants'd like to attend
        self.g = ([x for x in range(len(p))], []) # friends' graph

    def contains_tabu_elements(self, moves, lst):
        for m in moves:
            for e in lst:
                if m in e[1]:
                    return True
        return False

    def expire_features(self, lst):
        for i in range(len(lst)):
            lst[i][0] -= 1
        return [e for e in lst if e[0] > 0]

    def fitness(self, s):
        return self.fitness_friends(s) + self.fitness_max(s) + self.fitness_emin(s)

    def fitness_emin(self, s):
        total = 0
        for i in range(len(s)):
            score = 0
            for j in range(len(s[i])):
                score += s[i][j]
            score_ = score / self.emin[i] if self.emin[i] > 0 else 1
            total += score_ if score_ <= 1 else 1
        return total

    # objective: max amount of edges in the graph of connections between attending participants of each event
    def fitness_friends(self, s):
        v, e = self.g
        score = 0
        for j in range(len(s[0])):
            _v = [x for x in v]
            _e = [(x,y) for x, y in e]
            for i in range(len(s)):
                if s[i][j] == 0:
                    _v.remove(i)
                    _e = [(x,y) for x, y in _e if x != i and y != i]
            score += len(_e)
        return score

    # objective: maximize the total amount of participants
    def fitness_max(self, s):
        score = 0
        for i in range(len(s)):
            for j in range(len(s[i])):
                score += s[i][j]
        return score

    # objective: balance the |participants|/capacity ratio between all events
    def fitness_mean(self, s):
        score = float(1)
        cols = [0 for i in range(len(s[0]))]
        for i in range(len(s[0])):
            for j in range(len(s)):
                cols[i] += s[j][i]
            score *= float(cols[i]) / float(self.c[i]) if self.c[i] > 0 else float(1)
        return score

    def init_friends(self, pairs):
        self.g = ([x for x in range(len(self.p))], pairs)

    def locate_best_candidate(self, lst):
        best = lst[0]
        best_score = self.fitness(best[0])
        for candidate, moves in lst:
            candidate_score = self.fitness(candidate)
            if candidate_score > best_score:
                best = (candidate, moves)
                best_score = candidate_score
        return best

    def make_consistent(self):
        p_ = [[j for j in i] for i in self.p]
        c_ = [0 for i in self.c]
        # saving indices for futher use
        indices = [[] for i in range(len(p_))]
        for i in range(len(p_)):
            l = []
            for j in range(len(p_[i])):
                if p_[i][j] == 1:
                    indices[i].append(j)
                    c_[j] += 1
        # c-consistency
        for i in range(len(c_)):
            if c_[i] <= self.c[i]:
                continue
            for j in range(len(p_)):
                if c_[i] <= self.c[i]:
                    break
                if p_[j][i] == 1:
                    p_[j][i] = 0
                    c_[i] -= 1
        # d-consistency
        for i in range(len(indices)):
            if len(indices[i]) < 2: # if there's only one event, it can't overlap with another one
                continue
            for j in indices[i]:
                for k in indices[i]:
                    if not j == k and self.d[j][k] == 1: # overlapping, but not with itself
                        p_[i][j] = 0
        return p_

    def neighborhood(self, s):
        for i in range(len(self.p)):
            indices = [] # saving indices for checking d-consistency
            score = 0 # counting participations for checking emax-consistency
            for j in range(len(s[i])):
                if s[i][j] == 1:
                    indices.append(j)
                    score += 1
                    s_ = [[x for x in y] for y in s]
                    s_[i][j] = 0
                    print("REMOVE person %d from event %d" % (i, j))
                    # useless since it won't outperform the best solution found so far
                    yield (s_, [i]) # REMOVE
            for j in range(len(self.p[i])):
                if self.p[i][j] == 1 and s[i][j] == 0: # we'd like to improve that
                    # swap one person between two events
                    for k in range(len(self.p[i])):
                        if j != k and s[i][k] == 1:
                            s_ = [[x for x in y] for y in s]
                            s_[i][j] = 1
                            s_[i][k] = 0
                            indices_ = [x for x in indices]
                            indices_.pop(indices_.index(k))
                            # checking d-consistency
                            consistent = True
                            for l in indices_:
                                if j != l and self.d[j][l] == 1:
                                    consistent = False
                                    break
                            if consistent:
                                print("SWAP person %d from event %d to event %d" % (i, k, j))
                                yield (s_, [i]) # SWAP
                    if score == self.emax[i]: # checking emax-consistency
                        continue
                    # checking d-consistency
                    consistent = True
                    for k in indices:
                        if j != k and self.d[j][k] == 1:
                            consistent = False
                            break
                    if consistent:
                        # swap one event between two people
                        for k in range(len(self.p)):
                            if s[k][j] == 1:
                                s_ = [[x for x in y] for y in s]
                                s_[k][j] = 0
                                s_[i][j] = 1
                                print("SWAP event %d from person %d to person %d" % (j, k, i))
                                yield (s_, [i, k]) # SWAP
                    # checking c-consistency
                    if self.c[j] > 0: # capacity of event j is not infinite
                        capacity = 0
                        for k in range(len(s)):
                            capacity += s[k][j]
                        if capacity == self.c[j]:
                            continue
                    if consistent: # we've (strictly) improved the current solution
                        s_ = [[x for x in y] for y in s]
                        s_[i][j] = 1
                        print("ADD person %d to event %d" % (i, j))
                        yield (s_, [i]) # ADD

    def set_capacity(self, c):
        self.c = c

    def set_emax(self, emax):
        consistent = True
        for i in range(len(emax)):
            if emax[i] < self.emin[i]:
                consistent = False
                break
        if consistent:
            self.emax = emax

    def set_emin(self, emin):
        consistent = True
        for i in range(len(emin)):
            if emin[i] > self.emax[i]:
                consistent = False
                break
        if consistent:
            self.emin = emin

    def set_preferences(self, p):
        self.p = p

    def stopping_condition(self):
        self.MAX_TRY -= 1
        return self.MAX_TRY > 0

    def tabu(self):
        self.MAX_TRY = self.attemps
        # TODO: use a data structure to keep the indices instead of computing them everytime
        # TODO: use c as the remaining seats of events instead of capacities (be careful with unlimited events)
        s_best = self.make_consistent()
        s_best_score = self.fitness(s_best)
        tabu_list = []
        while self.stopping_condition():
            candidate_list = []
            for s_candidate, moves in self.neighborhood(s_best):
                if not self.contains_tabu_elements(moves, tabu_list):
                    candidate_list.append((s_candidate, moves))
            if len(candidate_list) == 0:
                print("no candidate")
                break
            s_candidate, moves = self.locate_best_candidate(candidate_list)
            s_candidate_score = self.fitness(s_candidate)
            tabu_list = self.expire_features(tabu_list)
            if s_candidate_score > s_best_score:
                tabu_list.append([self.attemps / 4, moves])
                s_best = s_candidate
                s_best_score = s_candidate_score
                while len(tabu_list) > self.MAX_SIZE:
                    tabu_list = self.expire_features(tabu_list)
            print("tabu_list: %s" % tabu_list)
            print("BEST: %s (%d)" % (s_best, s_best_score))
        self.MAX_TRY = self.attemps
        return s_best
