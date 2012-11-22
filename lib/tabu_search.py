#!/usr/bin/env python3

import random

status = None

class Status:

    '''
        input:
            _p: the preferences matrix
            _c: the capacities vector
            _d: the exclusion matrix
            _attempts: the number of iterations to perform
            _tenure: the number of iterations during which elements are tabu-active
    '''
    def __init__(self, p, c, d, attempts = 20, tenure = 2):
        self.p = p
        self.c = c
        self.d = d
        self.attempts = attempts
        self.tenure = tenure
        '''max number of events that participants would like to attend'''
        self.emax = []
        for p_ in p:
            participations = 0
            for participation in p_:
                participations += participation
            self.emax.append(participations)
        '''min number of events that participants would like to attend'''
        self.emin = [0 for p_ in p]

    '''
        Sets the max number of events that participants would like to attend.
        input:
            _emax: the new emax vector
    '''
    def set_emax(self, emax):
        assert len(emax) == len(self.emax)
        consistent = 1
        for i in range(len(emax)):
            if emax[i] < self.emin[i]:
                consistent = 0
                break
        if consistent:
            self.emax = emax

    '''
        Sets the min number of events that participants would like to attend.
        input:
            _emin: the new emin vector
    '''
    def set_emin(self, emin):
        assert len(emin) == len(self.emin)
        consistent = 1
        for i in range(len(emin)):
            if emin[i] > self.emax[i]:
                consistent = 0
                break
        if consistent:
            self.emin = emin

    '''
        Sets the global status reference to this instance.
    '''
    def set_status(self):
        global status
        status = self

'''
    Expires the elements that are no longer tabu-active.
    ! Acts in-place.
    input:
        _tabu: a list of (age, moves list) pairs
        _attemps: the number of iterations yet to perform
'''
def expire_features(tabu, attemps):
    while tabu and tabu[0][0] - attemps == status.tenure:
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
    Neighborhood generator.
    Generates the neighbors of a given solution, using the following operations:
        add - adding a participant to an event;
        move - moving a participant from an event to another one;
        remove - removing a participant from an event;
        replace - replacing a participant of an event by another one;
        swap - swapping two participants from two events.
    input:
        _s: a solution
    output:
        a set of (neighbor, moves) pairs
'''
def _neighborhood(s):
    assert len(s) == len(status.p)
    assert len(s[0]) == len(status.p[0])
    for i in range(len(status.p)):
        '''storing indices for checking consistency w.r.t. status.d matrix'''
        indices = []
        '''counting participations for checking consistency w.r.t. status.emax vector'''
        participations = 0
        for j in range(len(s[i])):
            if s[i][j] == 1:
                indices.append(j)
                participations += 1
                '''REMOVE'''
                s_ = [[x for x in y] for y in s]
                s_[i][j] = 0
                print("REMOVE participant {} from event {}".format(i, j))
                yield (s_, [i])
        for j in range(len(status.p[i])):
            if status.p[i][j] == 1 and s[i][j] == 0:
                '''MOVE'''
                for k in range(len(s[i])):
                    if j != k and s[i][k] == 1:
                        s_ = [[x for x in y] for y in s]
                        s_[i][j] = 1
                        s_[i][k] = 0
                        indices_ = indices[:]
                        indices_.pop(indices_.index(k))
                        '''checking consistency w.r.t. status.d matrix'''
                        consistent = 1
                        for l in indices_:
                            if j != l and status.d[j][l] == 1:
                                consistent = 0
                                break
                        if consistent:
                            print("MOVE participant {} from event {} to event {}".format(i, k, j))
                            yield (s_, [i])
                '''checking consistency w.r.t. status.emax vector'''
                if participations == status.emax[i]:
                    continue
                '''checking consistency w.r.t. status.d matrix'''
                consistent = 1
                for k in indices:
                    if j != k and status.d[j][k] == 1:
                        consistent = 0
                        break
                if consistent:
                    '''REPLACE'''
                    for k in range(len(s)):
                        if s[k][j] == 1:
                            s_ = [[x for x in y] for y in s]
                            s_[k][j] = 0
                            s_[i][j] = 1
                            print("REPLACE participant {} of event {} by participant {} ".format(k, j, i))
                            yield (s_, [i, k])
                '''checking consistency w.r.t. status.c vector'''
                '''capacity of event j is not infinite'''
                if status.c[j] > 0:
                    participations = 0
                    for k in range(len(s)):
                        participations += s[k][j]
                    if participations == status.c[j]:
                        continue
                if consistent:
                    '''ADD'''
                    s_ = [[x for x in y] for y in s]
                    s_[i][j] = 1
                    print("ADD participant {} to event {}".format(i, j))
                    yield (s_, [i])

def _objective_compound(s):
    return _objective_max(s) + _objective_emin(s)

'''
    Max objective function.
    Defines the score of a given solution by summing all the participations.
    input:
        _s: a solution
    output:
        the score of _s
'''
def _objective_max(s):
    score = 0
    for i in range(len(s)):
        for j in range(len(s[i])):
            score += s[i][j]
    return score

'''
    Min events participation objective function.
    Defines the score of a given solution by the consistency w.r.t. the status.emin vector (soft constraint).
    input:
        _s: a solution
    output:
        the score of _s
'''
def _objective_emin(s):
    total = 0
    for i in range(len(s)):
        score = 0
        for j in range(len(s[i])):
            score += s[i][j]
        score_ = score / status.emin[i] if status.emin[i] > 0 else 1
        total += score_ if score_ <= 1 else 1
    return total

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
    s_star_score = status.objective(s_legal[0][0])
    for s in s_legal:
        score = status.objective(s[0])
        if score == s_star_score:
            s_star.append(s)
        elif score > s_star_score:
            s_star = [s]
            s_star_score = score
    return s_star[random.randint(0, len(s_star) - 1)]

'''
    Performs a tabu search.
    input:
        _s: the initial solution
        _objective: the objective function to maximize
        _neighborhood: the neighborhood generator function
        _is_legal: the legal moves filter function
        _selection: the selection function
    output:
        the best solution found after _attemps iterations
'''
def tabu_search(s, objective=_objective_compound, neighborhood=_neighborhood, is_legal=_is_legal_not_tabu, selection=_selection_best):
    status.objective = objective
    s_star = s
    s_star_score = objective(s_star)
    tabu = []
    while status.attempts:
        s_legal = []
        for s_candidate, s_candidate_moves in neighborhood(s):
            if is_legal(s_candidate_moves, tabu):
                s_legal.append((s_candidate, s_candidate_moves))
        s, s_moves = selection(s_legal)
        s_score = objective(s)
        if s_score > s_star_score:
            s_star = s
            s_star_score = s_score
        tabu.append((status.attempts, s_moves))
        expire_features(tabu, status.attempts)
        status.attempts -= 1
    return s_star

