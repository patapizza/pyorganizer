#!/usr/bin/env python3

class Organizer:

    def __init__(self, p, c, d, attemps = 20):
        self.p = p
        self.c = c
        self.d = d
        self.queue = [[] for event in c]
        self.attemps = attemps # amount of times to iterate
        self.MAX_SIZE = 5 # size of the tabu list
        self.fitness_option = 0 # fitness function to use

    def contains_tabu_elements(self, candidate, lst):
        return candidate in lst

    def expire_features(self, lst):
        del lst[0]
        return lst

    def feature_differences(self, candidate, best):
        return candidate

    def fitness(self, s):
        if self.fitness_option == 0:
            return self.fitness_max(s)
        return self.fitness_mean(s)

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

    def locate_best_candidate(self, lst):
        best = lst[0]
        best_score = self.fitness(best)
        for candidate in lst:
            candidate_score = self.fitness(candidate)
            if candidate_score > best_score:
                best = candidate
                best_score = candidate_score
        return best

    def make_consistent(self):
        # we assume that p is c-consistent (because of the waiting list)
        # we still have to make it d-consistent
        p_ = [[j for j in i] for i in self.p]
        # saving indices for futher use
        indices = [[] for i in range(len(p_))]
        for i in range(len(p_)):
            l = []
            for j in range(len(p_[i])):
                if p_[i][j] == 1:
                    indices[i].append(j)
        for i in range(len(indices)):
            if len(indices[i]) < 2: # if there's only one event, it can't overlap with another one
                continue
            for j in indices[i]:
                for k in indices[i]:
                    if not j == k and self.d[j][k] == 1: # overlapping, but not with itself
                        p_[i][j] = 0
                        p_[i][k] = 0
        return p_

    def neighborhood(self, s):
        for i in range(len(self.p)):
            # saving indices for further use
            indices = []
            for j in range(len(s[i])):
                if s[i][j] == 1:
                    indices.append(j)
            for j in range(len(self.p[i])):
                if s[i][j] == 1 and self.p[i][j] == 0: # the preferences had been updated
                    s[i][j] = 0
                if self.p[i][j] == 1 and s[i][j] == 0: # we'd like to improve that
                    if self.c[j] > 0: # capacity of event j is not infinite
                        capacity = 0
                        for k in range(len(s)):
                            capacity += s[k][j]
                        if capacity == self.c[j]:
                            print("event %d is full (%d)" % (j, capacity))
                            continue
                    # checking d-consistency
                    consistent = True
                    for k in indices:
                        if j != k and self.d[j][k] == 1:
                            consistent = False
                            print("(%d,%d) not consistent" % (i, j))
                            break
                    if consistent: # we've (strictly) improved the current solution
                        s_ = [[x for x in y] for y in s]
                        s_[i][j] = 1
                        yield s_
                    # depending on objective, the following may be useless (symmetry)
                    else: # we can just swap two overlapping events
                        for k in indices:
                            if j != k and self.d[j][k] == 1: # overlapping, but not with itself
                                s_ = [[x for x in y] for y in s]
                                s_[i][j] = 1
                                s_[i][k] = 0
                                yield s_

    def set_capacity(self, c):
        self.c = c

    def set_preferences(self, p):
        self.p = p

    def stopping_condition(self):
        self.MAX_TRY -= 1
        return self.MAX_TRY > 0

    def subscription(self, e_index, p_index):
        attending = 0
        for i in range(len(self.p)):
            if self.p[i][e_index] == 1:
                attending += 1
        if attending == self.c[e_index]:
            self.queue[e_index].append(p_index)
        else:
            self.p[p_index][e_index] = 1

    def tabu(self):
        self.MAX_TRY = self.attemps
        # TODO: use a data structure to keep the indices instead of computing them everytime
        # TODO: use c as the remaining seats of events instead of capacities (be careful with unlimited events)
        s_best = self.make_consistent()
        s_best_score = self.fitness(s_best)
        tabu_list = []
        while self.stopping_condition():
            candidate_list = []
            for s_candidate in self.neighborhood(s_best):
                if not self.contains_tabu_elements(s_candidate, tabu_list):
                    candidate_list.append(s_candidate)
            if len(candidate_list) == 0:
                break
            s_candidate = self.locate_best_candidate(candidate_list)
            s_candidate_score = self.fitness(s_candidate)
            if s_candidate_score > s_best_score:
                s_best = s_candidate
                s_best_score = s_candidate_score
                tabu_list.append(self.feature_differences(s_candidate, s_best))
                while len(tabu_list) > self.MAX_SIZE:
                    self.expire_features(tabu_list)
        self.MAX_TRY = self.attemps
        return s_best

    def unsubscription(self, e_index, p_index):
        self.p[p_index][e_index] = 0
        attending = 0
        for i in range(len(self.p)):
            if self.p[i][e_index] == 1:
                attending += 1
        if attending == self.c[e_index] - 1 and self.queue[e_index]: # there's a new seat available
            self.p[self.queue[e_index].pop(0)][e_index] = 1
