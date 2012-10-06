#!/usr/bin/env python3

MAX_SIZE = 5

def contains_tabu_elements(candidate, lst):
    return candidate in lst

def expire_features(lst):
    del lst[0]
    return lst

def feature_differences(candidate, best):
    return candidate

def fitness(s):
    score = 0
    for i in range(len(s)):
        for j in range(len(s[i])):
            score += s[i][j]
    return score

def fitness_mean(s, c):
    score = float(1)
    cols = [0 for i in range(len(s[0]))]
    for i in range(len(s[0])):
        for j in range(len(s)):
            cols[i] += s[j][i]
        score *= float(cols[i]) / float(c[i]) if c[i] > 0 else float(1)
    print("fitness of %s :: %s :: %f" % (s, c, score))
    return score

def locate_best_candidate(lst):
    best = lst[0]
    best_score = fitness(best)
    for candidate in lst:
        candidate_score = fitness(candidate)
        if candidate_score > best_score:
            best = candidate
            best_score = candidate_score
    return best

def make_consistent(p, c, d):
    # we assume that p is c-consistent (because of the waiting list)
    # we still have to make it d-consistent
    p_ = [[j for j in i] for i in p]
    indices = [[] for i in range(len(p_))]
    for i in range(len(p_)):
        l = []
        for j in range(len(p_[i])):
            if p_[i][j] == 1:
                indices[i].append(j)
    for i in range(len(indices)):
        if len(indices[i]) < 2:
            continue
        for j in indices[i]:
            for k in indices[i]:
                if not j == k and d[j][k] == 1:
                    p_[i][j] = 0
                    p_[i][k] = 0
    return p_

def neighborhood(s, p, c, d):
    for i in range(len(p)):
        indices = []
        for j in range(len(s[i])):
            if s[i][j] == 1:
                indices.append(j)
        for j in range(len(p[i])):
            if p[i][j] == 1 and s[i][j] == 0:
                if c[j] > 0: # capacity of event j is not infinite
                    capacity = 0
                    for k in range(len(s)):
                        capacity += s[k][j]
                    if capacity == c[j]:
                        print("event %d is full (%d)" % (j, capacity))
                        continue
                consistent = True
                for k in indices:
                    if j != k and d[j][k] == 1:
                        consistent = False
                        print("(%d,%d) not consistent" % (i,j))
                        break
                if consistent:
                    s_ = [[x for x in y] for y in s]
                    s_[i][j] = 1
                    yield s_
                else: # depending on objective, may be useless (symmetries)
                    for k in indices:
                        if j != k and d[j][k] == 1:
                            s_ = [[x for x in y] for y in s]
                            s_[i][j] = 1
                            s_[i][k] = 0
                            yield s_

def tabu(p, c, d, attemps = 20):
    global MAX_TRY
    MAX_TRY = attemps
    # todo: use a data structure to keep the indices instead of computing them everytime
    # todo: use c as the remaining places of events instead of capacities
    s_best = make_consistent(p, c, d)
    s_best_score = fitness(s_best)
    tabu_list = []
    while stopping_condition():
        candidate_list = []
        for s_candidate in neighborhood(s_best, p, c, d):
            if not contains_tabu_elements(s_candidate, tabu_list):
                candidate_list.append(s_candidate)
        if len(candidate_list) == 0:
            break
        s_candidate = locate_best_candidate(candidate_list)
        s_candidate_score = fitness(s_candidate)
        if s_candidate_score > s_best_score:
            s_best = s_candidate
            s_best_score = s_candidate_score
            tabu_list.append(feature_differences(s_candidate, s_best))
            while len(tabu_list) > MAX_SIZE:
                expire_features(tabu_list)
    MAX_TRY = attemps
    return s_best

def stopping_condition():
    global MAX_TRY
    MAX_TRY -= 1
    return MAX_TRY > 0
