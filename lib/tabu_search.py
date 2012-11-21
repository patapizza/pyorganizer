#!/usr/bin/env python3

import random

'''
    parameters to define:
        attemps - the number of iterations to perform
        tenure - the number of iterations during which elements are tabu-active
'''

'''
    Expires the elements that are no longer tabu-active.
    ! Acts in-place.
    input:
        _tabu: a list of (age, moves list) pairs
        _attemps: the number of iterations yet to perform
'''
def expire_features(tabu, attemps):
    while tabu and tabu[0][0] - attemps == tenure:
        del tabu[0]

'''
    Restricts the neighborhood by forbidding candidates having tabu-active elements.
    input:
        _s_candidate_moves: a list of moves
        _tabu: a list of (age, moves list) pairs
    output:
        0 if a move of _s_candidate_moves is tabu
        1 otherwise
'''
def _is_legal_not_tabu(s_candidate_moves, tabu):
    tabu_ = [element[1] for element in tabu]
    for s_candidate_move in s_candidate_moves:
        if s_candidate_move in tabu_:
            return 0
    return 1

'''
    Restricts the neighborhood but considers candidates better than the optimum solution found so far.
    input:
        _s_neighbor: a (s_candidate, s_candidate_moves) pair
        _tabu: a list of (age, moves list) pairs
    output:
        0 if _s_candidate is not better than s_star and if a move of _s_candidate_moves is tabu
        1 otherwise
'''
def _is_legal_not_tabu_aspiration(s_neighbor, tabu):
    s_candidate, s_candidate_moves = s_neighbor
    return objective(s_candidate) > objective(s_star) or _is_legal_not_tabu(s_candidate_moves, tabu)

'''
    Performs a tabu search.
    input:
        _objective: the objective function to maximize
        _neighborhood: the neighborhood generator function
        _is_legal: the legal moves filter function
        _selection: the selection function
        _s: the initial solution
    output:
        the best solution found after _attemps iterations
'''
def tabu_search(objective, neighborhood, is_legal, selection, s):
    s_star = s
    s_star_score = objective(s_star)
    tabu = []
    while attemps:
        s_score = objective(s)
        if satisfiable(s) and s_score > s_star_score:
            s_star = s
            s_star_score = s_score
        s_legal = []
        for s_candidate, s_candidate_moves in neighborhood(s):
            if is_legal(s_moves, tabu):
                s_legal.append((s_candidate, s_candidate_moves))
        s, s_moves = selection(s_legal)
        tabu.append((attempts, s_moves))
        expire_features(tabu, attemps)
        attemps -= 1
    return s_star

'''
operations:
    add - adding a participant to an event
    move - moving a participant from an event to another one
    remove - removing a participant from an event
    replace - replacing a participant at an event by another one
    swap - swapping two participants from two events
input:
    _s: a solution
output:
    a set of (neighbor, moves) pairs
'''
def _neighborhood(s):
    pass

'''
    Objective function.
    Defines the score of a given solution.
    input:
        _s: a solution
    output:
        the score of _s
'''
def _objective(s):
    pass

'''
    Selection function of the Best-Neighbor heuristic.
    Chooses the neighbor with the best evaluation.
    input:
        _s_legal: a list of (solution, moves) pairs
    output:
        a pair among _s_legal for which the objective is maximum, uniformly randomly
'''
def _selection_best(s_legal):
    s_star = [s_legal[0]]
    s_star_score = objective(s_legal[0][0])
    for s in s_legal:
        score = objective(s[0])
        if score == s_star_score:
            s_star.append(s)
        elif score > s_star_score:
            s_star = [s]
            s_star_score = score
    return s_star[random.randint(0, len(s_star) - 1)]
