#!/usr/bin/env python3

import random

verbose = 0
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
        self.emax = [sum(ppp for ppp in pp) for pp in p]
        '''min number of events that participants would like to attend'''
        self.emin = [0] * len(p)
        '''close friends' adjacency matrix'''
        self.cf = [[0] * len(p)] * len(p)

    '''
        Sets the close friends' adjacency matrix.
        input:
            _cf: the new matrix
    '''
    def set_cf(self, cf):
        assert len(cf) == len(self.cf)
        assert len(cf[0]) == len(self.cf[0])
        self.cf = cf

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
        _tabu: a list of (age, move) pairs
        _attemps: the number of iterations yet to perform
'''
def expire_features(tabu, attemps):
    while tabu and tabu[0][0] - attemps == status.tenure:
        del tabu[0]

'''
    Builds an initial solution from 0's matrix toward preferences' matrix.
    input:
        _p: the preferences' matrix
        _c: the max capacity vector
        _d: the exclusion matrix
    output:
        a consistent solution
'''
def initial_solution_bottom_up(p, c, d):
    '''TODO: check if it's full instead of limited number of attempts'''
    s = [[0] * len(p[0]) for pp in p]
    capacity = [0] * len(c)
    d_indices = [[i for i in range(len(j)) if j[i] == 1] for j in d]
    attempts = 5
    while attempts > 0:
        col, row = -1, -1
        while 1:
            row = random.randint(0, len(s) - 1)
            col = random.randint(0, len(s[0]) - 1)
            if p[row][col] == 1 and s[row][col] == 0:
                break
        attempts -= 1
        if c[col] == 0 or capacity[col] < c[col]:
            indices = [j for j in range(len(s[row])) if s[row][j] == 1]
            if len(set(indices) & set(d_indices[col])) == 0:
                s[row][col] = 1
                capacity[col] += 1
                attempts = 5
    return s


'''
    Builds an initial solution descending from preferences' matrix.
    input:
        _p: the preferences' matrix
        _c: the max capacity vector
        _d: the exclusion matrix
    output:
        a consistent solution
'''
def initial_solution_top_down(p, c, d):
    '''TODO: implement new algorithm
    1. store indices where p[i][j] = 1
    2. remove where max capacity attained, randomly until consistent
    3. make it d-consistent randomly for each line'''
    s = [ss[:] for ss in p]
    '''making it consistent against max capacity vector'''
    for j in range(len(s[0])):
        capacity = 0
        indices = []
        for i in range(len(s)):
            capacity += s[i][j]
            indices.append(i)
        '''TODO: shuffle indices instead of undefinitely looping!'''
        while capacity > c[j]:
            r = random.randint(0, len(indices) - 1)
            if s[r][j] == 1:
                capacity -= 1
                s[r][j] = 0
    '''making it consistent against exclusion matrix'''
    d_indices = [[i for i in range(len(j)) if j[i] == 1] for j in d]
    for i in range(len(s)):
        indices = [j for j in range(len(s[i])) if s[i][j] == 1]
        for k in indices:
            inter = set(indices) & set(d_indices[k])
            while len(inter) > 1:
                event = inter.pop()
                s[i][event] = 0
                indices.remove(event)
    return s

'''
    Checks consistency against status.c vector.
    input:
        _i: an event
        _s: a solution
    output:
        1 if event _i isn't full yet in _s
        0 otherwise
'''
def is_c_consistent(i, s):
    '''capacity of event _i is infinite'''
    if status.c[i] == 0:
        return 1
    participations = 0
    for j in range(len(s)):
        participations += s[j][i]
        if participations == status.c[i]:
            return 0
    return 1
    
'''
    Checks consistency w.r.t. status.d matrix.
    input:
        _i: index of an event
        _indices: vector of attending events
    output:
        1 if event _i is not exclusive with any event of _indices
        0 otherwise
'''
def is_d_consistent(i, indices):
    for j in indices:
        if i != j and status.d[i][j] == 1:
            return 0
    return 1

'''
    Restricts the neighborhood by forbidding candidates having tabu-active elements.
    input:
        _s_candidate_moves: a list of moves
        _tabu: a list of (age, move) pairs
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
        0 if _s_candidate is not better than status.s_star and if a move of _s_candidate_moves is tabu
        1 otherwise
'''
def _is_legal_not_tabu_aspiration(s_neighbor, tabu):
    s_candidate, s_candidate_moves = s_neighbor
    return status.objective(s_candidate) > status.s_star_score or _is_legal_not_tabu(s_candidate_moves, tabu)

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
        indices = []
        participations = 0
        for j in range(len(s[i])):
            if s[i][j] == 1:
                indices.append(j)
                participations += 1
                '''REMOVE'''
                s_ = [ss[:] for ss in s]
                s_[i][j] = 0
                if verbose:
                    print("REMOVE participant {} from event {}".format(i, j))
                yield (s_, [i])
        for j in range(len(status.p[i])):
            if status.p[i][j] == 1 and s[i][j] == 0:
                if participations > 0:
                    c_consistency_checked = 0
                    c_consistent = 0
                    for k in range(len(s[i])):
                        if k != j and s[i][k] == 1:
                            indices_ = indices[:]
                            indices_.pop(indices_.index(k))
                            if not is_d_consistent(j, indices_):
                                continue
                            if not c_consistency_checked:
                                c_consistency_checked = 1
                                c_consistent = is_c_consistent(j, s)
                            if c_consistent:
                                '''MOVE'''
                                s_ = [ss[:] for ss in s]
                                s_[i][j] = 1
                                s_[i][k] = 0
                                if verbose:
                                    print("MOVE participant {} from event {} to event {}".format(i, k, j))
                                yield (s_, [i])
                            '''SWAP'''
                            for ii in range(len(status.p)):
                                if ii != i and status.p[ii][k] == 1 and s[ii][k] == 0 and s[ii][j] == 1:
                                    s_ = [ss[:] for ss in s]
                                    s_[i][j] = 1
                                    s_[i][k] = 0
                                    s_[ii][k] = 1
                                    s_[ii][j] = 0
                                    d_consistent = 1
                                    '''checking that event _jj is not exclusive with any other attending event'''
                                    for jj in range(len(s_[ii])):
                                        if jj != k and s_[ii][jj] == 1 and status.d[jj][k] == 1:
                                            d_consistent = 0
                                            break
                                    if d_consistent:
                                        if verbose:
                                            print("SWAP participant {} of event {} with participant {} of event {}".format(i, j, ii, k))
                                        yield (s_, [i, ii])
                '''checking that participant _i hasn't reached his max attending events' boundary yet'''
                if participations == status.emax[i]:
                    continue
                d_consistent = is_d_consistent(j, indices)
                if d_consistent:
                    '''REPLACE'''
                    for k in range(len(s)):
                        if s[k][j] == 1:
                            s_ = [ss[:] for ss in s]
                            s_[k][j] = 0
                            s_[i][j] = 1
                            if verbose:
                                print("REPLACE participant {} of event {} by participant {} ".format(k, j, i))
                            yield (s_, [i, k])
                if not is_c_consistent(j, s):
                    continue
                if d_consistent:
                    '''ADD'''
                    s_ = [ss[:] for ss in s]
                    s_[i][j] = 1
                    if verbose:
                        print("ADD participant {} to event {}".format(i, j))
                    yield (s_, [i])

'''
    Compound objective function.
    input:
        _s: a solution
    output:
        the score of _s
'''
def _objective_compound(s):
    return _objective_max(s) + _objective_emin(s) + _objective_friends(s)

'''
    Max close friends objective function.
    Defines the score of a given solution by summing the "friendship relations" between participants.
    input:
        _s: a solution
    output:
        the score of _s
'''
def _objective_friends(s):
    score = 0
    for j in range(len(s[0])):
        participants = [i for i in range(len(s)) if s[i][j] == 1]
        for p in participants:
            for p_ in participants:
                if p != p_:
                    score += status.cf[p][p_]
                    score += status.cf[p_][p]
    return score


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
    for ss in s:
        score += sum(sss for sss in ss)
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
        score_ = sum(ss for ss in s[i]) / status.emin[i] if status.emin[i] > 0 else 1
        total += min(1, score_)
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
        the best solution found after _attemps iterations and its score as a pair
'''
def tabu_search(s, objective=_objective_compound, neighborhood=_neighborhood, is_legal=_is_legal_not_tabu, selection=_selection_best):
    status.objective = objective
    status.s_star = s
    status.s_star_score = objective(status.s_star)
    tabu = []
    while status.attempts:
        s_legal = [(s_candidate, s_candidate_moves) for s_candidate, s_candidate_moves in neighborhood(s) if is_legal(s_candidate_moves, tabu)]
        s, s_moves = selection(s_legal)
        s_score = objective(s)
        if s_score > status.s_star_score:
            status.s_star = s
            status.s_star_score = s_score
        for s_move in s_moves:
            tabu.append((status.attempts, s_move))
        expire_features(tabu, status.attempts)
        status.attempts -= 1
    return (status.s_star, status.s_star_score)

