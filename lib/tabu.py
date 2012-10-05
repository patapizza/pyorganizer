#!/usr/bin/env python3

MAX_SIZE = 10

def contains_tabu_elements(candidate, lst):
    pass

def expire_features(lst):
    pass

def feature_differences(candidate, best):
    pass

def fitness(candidate):
    pass

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

def make_initial_solution(s):
    pass

def neighborhood(s):
    pass

def tabu(participants):
    s_best = make_consistent(participants)
    # s_best = make_initial_solution(s_best)
    s_best_score = fitness(s_best)
    tabu_list = []
    while stopping_condition():
        candidate_list = []
        for s_candidate in neighborhood(s_best):
            if not contains_tabu_elements(s_candidate, tabu_list):
                tabu_list.append(s_candidate)
        s_candidate = locate_best_candidate(candidate_list)
        s_candidate_score = fitness(s_candidate)
    if s_candidate_score > s_best_score:
        s_best = s_candidate
        s_best_score = s_candidate_score
        tabu_list.append(feature_differences(s_candidate, s_best))
        while len(tabu_list) > MAX_SIZE:
            expire_features(tabu_list)
    return s_best

def stopping_condition():
    pass
