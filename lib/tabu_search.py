#!/usr/bin/env python3

import random

verbose = 0
status = None

class Score:
    
    '''
        input:
            _objective: the objective function
            _total: the actual score
            _params: a list of parameters needed for incrementality
    '''
    def __init__(self, objective, total = 0, params = []):
        self.objective = objective
        self.total = total
        self.params = params

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
        '''setting k default value for the best-k-neighbors selection heuristic'''
        self.k = 5
        '''age of participants'''
        self.age = [0] * len(p)
        '''aimed median age for events'''
        self.mage = [0] * len(p[0])
        '''sex of participants; 1 is male, 0 is female'''
        self.male = [0] * len(p)
        '''aimed sex ratio for events'''
        self.sratio = [0] * len(p[0])
        '''min capacity aimed for events'''
        self.cmin = [0] * len(p[0])

    '''
        Sets the age vector of participants.
        input:
            _age: the new age vector
    '''
    def set_age(self, age):
        assert len(age) == len(self.age)
        self.age = age

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
        Sets the min capacity vector for events.
        input:
            _cmin: the new cmin vector
    '''
    def set_cmin(self, cmin):
        assert len(cmin) == len(self.cmin)
        for j in range(len(cmin)):
            if self.c[j] > 0:
                assert cmin[j] <= self.c[j]
        self.cmin = cmin

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
        Sets the aimed median age vector for events.
        input:
            _mage: the new mage vector
    '''
    def set_mage(self, mage):
        assert len(mage) == len(self.mage)
        self.mage = mage

    '''
        Sets the male vector for participants.
        input:
            _male: the new male vector
    '''
    def set_male(self, male):
        assert len(male) == len(self.male)
        for i in male:
            assert i == 0 or i == 1
        self.male = male

    '''
        Sets the aimed sex ratio vector for events.
        input:
            _sratio: the new sratio vector
    '''
    def set_sratio(self, sratio):
        assert len(sratio) == len(self.sratio)
        for i in sratio:
            assert i >= 0 and i <= 1
        self.sratio = sratio

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
    Extracts participants indices from a move structure.
    input:
        _s_move: a move in the form (op_name, indices tuple)
    output:
        a list of participants indices from _s_move
'''
def extract_tabu_elements(s_move):
    if s_move[0] == 'add' or s_move[0] == 'remove' or s_move[0] == 'move':
        return [s_move[1][0]]
    return [s_move[1][0], s_move[1][1]]

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
    '''TODO: against emax instead of c'''
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
    '''TODO: against emax instead of c'''
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
        _s_neighbor: a (s_candidate, s_candidate_move) pair
        _tabu: a list of (age, move) pairs
    output:
        0 if a move of _s_neighbor[1] is tabu
        1 otherwise
'''
def is_legal_not_tabu(s_neighbor, tabu):
    tabu_ = [element[1] for element in tabu]
    for s_candidate_move in extract_tabu_elements(s_neighbor[1]):
        if s_candidate_move in tabu_:
            return 0
    return 1

'''
    Restricts the neighborhood but considers candidates better than the optimum solution found so far.
    input:
        _s_neighbor: a (s_candidate, s_candidate_move) pair
        _tabu: a list of (age, moves list) pairs
    output:
        0 if _s_candidate is not better than status.s_star and if a move of _s_candidate_moves is tabu
        1 otherwise
'''
def is_legal_not_tabu_aspiration(s_neighbor, tabu):
    return is_legal_not_tabu(s_neighbor, tabu) or status.objective(status.s_, status.s_score, s_neighbor[1]).total > status.s_star_score.total

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
        a set of (neighbor, move) pairs
'''
def neighborhood_all(s):
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
                yield (s_, ('remove', (i, j)))
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
                                yield (s_, ('move', (i, k, j)))
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
                                            print("SWAP participant {} of event {} with participant {} of event {}".format(i, k, ii, j))
                                        yield (s_, ('swap', (i, ii, k, j)))
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
                            yield (s_, ('replace', (k, i, j)))
                if not is_c_consistent(j, s):
                    continue
                if d_consistent:
                    '''ADD'''
                    s_ = [ss[:] for ss in s]
                    s_[i][j] = 1
                    if verbose:
                        print("ADD participant {} to event {}".format(i, j))
                    yield (s_, ('add', (i, j)))
'''
    Min participants objective function.
    Defines the score of a given solution as the number of extra participants, i.e. over the cmin limit.
    input:
        _s: a solution
    output:
        the score of _s (Score object)
'''
def objective_cmin(s):
    score = Score(objective_cmin_incr)
    for j in range(len(s[0])):
        a = (sum(s[i][j] for i in range(len(s))) / status.cmin[j]) if status.cmin[j] > 0 else 1
        score.params.append(a)
        score.total += min(1, a)
    return score

'''
    Min participants objective function (incremental version).
    Defines the score of a given solution as the number of extra participants, i.e. over the cmin limit.
    input:
        _s: a solution
    output:
        the score of _s (Score object)
'''
def objective_cmin_incr(s, score, move):
    score_ = Score(score.objective, score.total, score.params)
    #print("{} {}".format(score_.total, objective_cmin(s).total))
    #print(move)
    if move[0] == 'add':
        '''
            ('add', (participant i, event j))
        '''
        a = score_.params[move[1][1]]
        new_a = (a + 1 / status.cmin[move[1][1]]) if status.cmin[move[1][1]] > 0 else 1
        score_.total = score_.total - min(1, a) + min(1, new_a)
        score_.params[move[1][1]] = new_a
    elif move[0] == 'remove':
        '''
            ('remove', (participant i, event j))
        '''
        a = score_.params[move[1][1]]
        new_a = (a - 1 / status.cmin[move[1][1]]) if status.cmin[move[1][1]] > 0 else 1
        score_.total = score_.total - min(1, a) + min(1, new_a)
        score_.params[move[1][1]] = new_a
    elif move[0] == 'move':
        '''
            ('move', (participant i, event j1, event j2))
            -> ('remove', (i, j1)) + ('add', (i, j2))
        '''
        score_ = objective_cmin_incr(s, score_, ('remove', (move[1][0], move[1][1])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][1]] = 0
        score_ = objective_cmin_incr(s_, score_, ('add', (move[1][0], move[1][2])))
    elif move[0] == 'replace':
        '''
            ('replace', (participant i1, participant i2, event j))
            -> ('remove', (i1, j)) + ('add', (i2, j))
        '''
        score_ = objective_cmin_incr(s, score_, ('remove', (move[1][0], move[1][2])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        score_ = objective_cmin_incr(s_, score_, ('add', (move[1][1], move[1][2])))
    elif move[0] == 'swap':
        '''
            ('swap', (participant i1, participant i2, event j1, event j2))
            -> ('move', (i1, j1, j2)) + ('move', (i2, j2, j1))
        '''
        score_ = objective_cmin_incr(s, score_, ('move', (move[1][0], move[1][2], move[1][3])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        s_[move[1][0]][move[1][3]] = 1
        score_ = objective_cmin_incr(s_, score_, ('move', (move[1][1], move[1][3], move[1][2])))
    return score_

'''
    Compound objective function.
    input:
        _s: a solution
    output:
        the score of _s (Score object)
'''
def objective_compound(s):
    score = Score(objective_compound_incr)
    score.subscores = []
    subscore = objective_max(s)
    subscore.weight = 0.25
    score.total += (subscore.weight * subscore.total)
    score.subscores.append(subscore)
    subscore = objective_emin(s)
    subscore.weight = 0.25
    score.total += (subscore.weight * subscore.total)
    score.subscores.append(subscore)
    '''! FIXME objective_emin and objective_cmin not consistent neither!'''
    '''! FIXME objective_median_age and objective_sex_ratio not consistent'''
    '''subscore = objective_median_age(s)
    score.total += subscore.total
    score.subscores.append(subscore)
    subscore = objective_sex_ratio(s)
    score.total += subscore.total
    score.subscores.append(subscore)'''
    subscore = objective_cmin(s)
    subscore.weight = 0.25
    score.total += (subscore.weight * subscore.total)
    score.subscores.append(subscore)
    subscore = objective_friends(s)
    subscore.weight = 0.25
    score.total += (subscore.weight * subscore.total)
    score.subscores.append(subscore)
    print("s_init compounded score: {}".format(score.total))
    return score


'''
    Compound objective function (incremental version).
    input:
        _s: a solution
        _score: the score of _s (Score object)
        _move: a (operation_name, involved participants/events tuple) pair
    output:
        the score of _s after performing the move _move (Score object)
'''
def objective_compound_incr(s, score, move):
    score_ = Score(score.objective, 0, score.params)
    subscores = []
    for subscore in score.subscores:
        subscore_ = subscore.objective(s, subscore, move)
        subscore_.weight = subscore.weight
        score_.total += (subscore_.weight * subscore_.total)
        subscores.append(subscore_)
    score_.subscores = subscores
    return score_

'''
    Min events participation objective function.
    Defines the score of a given solution by the consistency w.r.t. the status.emin vector (soft constraint).
    input:
        _s: a solution
    output:
        the score of _s (Score object)
'''
def objective_emin(s):
    score = Score(objective_emin_incr)
    score.params = []
    for i in range(len(s)):
        a = (sum(ss for ss in s[i]) / status.emin[i]) if status.emin[i] > 0 else 1
        score.params.append(a)
        score.total += min(1, a)
    return score

'''
    Min events participation objective function (incremental version).
    Defines the score of a given solution by the consistency w.r.t. the status.emin vector (soft constraint).
    input:
        _s: a solution
        _score: the score of _s (Score object)
        _move: a (operation_name, involved participants/events tuple) pair
    output:
        the score of _s after performing the move _move (Score object)
'''
def objective_emin_incr(s, score, move):
    score_ = Score(score.objective, score.total, score.params)
    #print("{} {}".format(score_.total, objective_emin(s).total))
    #print(move)
    if move[0] == 'add':
        '''
            ('add', (participant i, event j))
        '''
        print("ADD-- BEFORE: {} ({})".format(objective_emin(s).total, score_.total))
        a = score_.params[move[1][0]]
        new_a = (a + 1 / status.emin[move[1][0]]) if status.emin[move[1][0]] > 0 else 1
        score_.total = score_.total - min(1, a) + min(1, new_a)
        score_.params[move[1][0]] = new_a 
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][1]] = 1
        print("ADD-- AFTER: {} ({})".format(objective_emin(s_).total, score_.total))
    elif move[0] == 'remove':
        '''
            ('remove', (participant i, event j))
        '''
        print("REMOVE-- BEFORE: {} ({})".format(objective_emin(s).total, score_.total))
        a = score_.params[move[1][0]]
        new_a = (a - 1 / status.emin[move[1][0]]) if status.emin[move[1][0]] > 0 else 1
        score_.total = score_.total - min(1, a) + min(1, new_a)
        score_.params[move[1][0]] = new_a
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][1]] = 0
        print("REMOVE-- AFTER: {} ({})".format(objective_emin(s_).total, score_.total))
    elif move[0] == 'move':
        '''
            ('move', (participant i, event j1, event j2))
            -> ('remove', (i, j1)) + ('add', (i, j2))
        '''
        print("MOVE-- BEFORE: {} ({})".format(objective_emin(s).total, score_.total))
        #print("MOVE-- before remove: {}".format(score_.total))
        score_ = objective_emin_incr(s, score_, ('remove', (move[1][0], move[1][1])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][1]] = 0
        print("MOVE-- score after remove: {} ({})".format(score_.total, objective_emin(s_).total))
        score_ = objective_emin_incr(s_, score_, ('add', (move[1][0], move[1][2])))
        s_[move[1][0]][move[1][2]] = 1
        #print("MOVE-- score after add: {}".format(score_.total))
        print("MOVE-- AFTER: {} ({})".format(objective_emin(s_).total, score_.total))
    elif move[0] == 'replace':
        '''
            ('replace', (participant i1, participant i2, event j))
            -> ('remove', (i1, j)) + ('add', (i2, j))
        '''
        print("REPLACE-- BEFORE: {} ({})".format(objective_emin(s).total, score_.total))
        score_ = objective_emin_incr(s, score_, ('remove', (move[1][0], move[1][2])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        score_ = objective_emin_incr(s_, score_, ('add', (move[1][1], move[1][2])))
        s_[move[1][1]][move[1][2]] = 1
        print("REPLACE-- AFTER: {} ({})".format(objective_emin(s_).total, score_.total))
    elif move[0] == 'swap':
        '''
            ('swap', (participant i1, participant i2, event j1, event j2))
            -> ('move', (i1, j1, j2)) + ('move', (i2, j2, j1))
        '''
        score_ = objective_emin_incr(s, score_, ('move', (move[1][0], move[1][2], move[1][3])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        s_[move[1][0]][move[1][3]] = 1
        score_ = objective_emin_incr(s_, score_, ('move', (move[1][1], move[1][3], move[1][2])))
    return score_

'''
    Max close friends objective function.
    Defines the score of a given solution by summing the "friendship relations" between participants.
    input:
        _s: a solution
    output:
        the score of _s (Score object)
'''
def objective_friends(s):
    score = Score(objective_friends_incr)
    for j in range(len(s[0])):
        for i in range(len(s)):
            for k in range(len(s)):
                if i != k:
                    score.total += (status.cf[i][k] * s[i][j] * s[k][j])
    return score

'''
    Max close friends objective function (incremental version).
    Defines the score of a given solution by summing the "friendship relations" between participants.
    input:
        _s: a solution
        _score: the score of _s (Score object)
        _move: a (operation_name, involved participants/events tuple) pair
    output:
        the score of _s after performing the move _move (Score object)
'''
def objective_friends_incr(s, score, move):
    score_ = Score(score.objective, score.total, score.params)
    if move[0] == 'add':
        '''
            ('add', (participant i, event j))
        '''
        score_.total += sum((status.cf[move[1][0]][k] + status.cf[k][move[1][0]]) * s[k][move[1][1]] for k in range(len(s)) if k != move[1][0])
    elif move[0] == 'remove':
        '''
            ('remove', (participant i, event j))
        '''
        score_.total -= sum((status.cf[move[1][0]][k] + status.cf[k][move[1][0]]) * s[k][move[1][1]] for k in range(len(s)) if k != move[1][0])
    elif move[0] == 'move':
        '''
            ('move', (participant i, event j1, event j2))
            -> ('remove', (i, j1)) + ('add', (i, j2))
        '''
        score_ = objective_friends_incr(s, score_, ('remove', (move[1][0], move[1][1])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][1]] = 0
        score_ = objective_friends_incr(s_, score_, ('add', (move[1][0], move[1][2])))
    elif move[0] == 'replace':
        '''
            ('replace', (participant i1, participant i2, event j))
            -> ('remove', (i1, j)) + ('add', (i2, j))
        '''
        score_ = objective_friends_incr(s, score_, ('remove', (move[1][0], move[1][2])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        score_ = objective_friends_incr(s_, score_, ('add', (move[1][1], move[1][2])))
    elif move[0] == 'swap':
        '''
            ('swap', (participant i1, participant i2, event j1, event j2))
            -> ('move', (i1, j1, j2)) + ('move', (i2, j2, j1))
        '''
        score_ = objective_friends_incr(s, score_, ('move', (move[1][0], move[1][2], move[1][3])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        s_[move[1][0]][move[1][3]] = 1
        score_ = objective_friends_incr(s_, score_, ('move', (move[1][1], move[1][3], move[1][2])))
    return score_

'''
    Max objective function.
    Defines the score of a given solution by summing all the participations.
    input:
        _s: a solution
    output:
        the score of _s (Score object)
'''
def objective_max(s):
    score = Score(objective_max_incr)
    for ss in s:
        score.total += sum(sss for sss in ss)
    return score

'''
    Max objective function (incremental version).
    Defines the score of a given solution by summing all the participations.
    input:
        _s: a solution
        _score: the score of _s (Score object)
        _move: a (operation_name, involved participants/events tuple) pair
    output:
        the score of _s after performing the move _move (Score object)
'''
def objective_max_incr(s, score, move):
    score_ = Score(score.objective, score.total, score.params)
    if move[0] == 'add':
        '''
            ('add', (participant i, event j))
        '''
        score_.total += status.p[move[1][0]][move[1][1]]
    elif move[0] == 'remove':
        '''
            ('remove', (participant i, event j))
        '''
        score_.total -= status.p[move[1][0]][move[1][1]]
    elif move[0] == 'move':
        '''
            ('move', (participant i, event j1, event j2))
            -> ('remove', (i, j1)) + ('add', (i, j2))
        '''
        score_ = objective_max_incr(s, score_, ('remove', (move[1][0], move[1][1])))
        score_ = objective_max_incr(s, score_, ('add', (move[1][0], move[1][2])))
    elif move[0] == 'replace':
        '''
            ('replace', (participant i1, participant i2, event j))
            -> ('remove', (i1, j)) + ('add', (i2, j))
        '''
        score_ = objective_max_incr(s, score_, ('remove', (move[1][0], move[1][2])))
        score_ = objective_max_incr(s, score_, ('add', (move[1][1], move[1][2])))
    elif move[0] == 'swap':
        '''
            ('swap', (participant i1, participant i2, event j1, event j2))
            -> ('move', (i1, j1, j2)) + ('move', (i2, j2, j1))
        '''
        score_ = objective_max_incr(s, score_, ('move', (move[1][0], move[1][2], move[1][3])))
        score_ = objective_max_incr(s, score_, ('move', (move[1][1], move[1][3], move[1][2])))
    return score_

'''
    Median age objective function.
    Defines the score (cost) of a given solution by its distance w.r.t. the mage vector.
    input:
        _s: a solution
    output:
        the score of _s (Score object)
'''
def objective_median_age(s):
    score = Score(objective_median_age_incr)
    for j in range(len(s[0])):
        a, b = 0, 0
        for i in range(len(s)):
            if status.age[i] > 0:
                a += (s[i][j] * status.age[i])
                b += s[i][j]
        score.params.append([a, b])
        if status.mage[j] > 0:
            score.total -= abs(a / b - status.mage[j]) if b > 0 else status.mage[j]
    return score

'''
    Median age objective function (incremental version).
    Defines the score of a given solution by its distance w.r.t. the mage vector.
    input:
        _s: a solution
        _score: the score of _s (Score object)
        _move: a (operation_name, involved participants/events tuple) pair
    output:
        the score of _s after performing the move _move (Score object)
'''
def objective_median_age_incr(s, score, move):
    score_ = Score(score.objective, score.total, score.params)
    #print("{} : {}".format(score_.total, objective_median_age(s).total))
    print(move)
    if move[0] == 'add':
        '''
            ('add', (participant i, event j))
        '''
        if status.age[move[1][0]] > 0:
            a, b = score_.params[move[1][1]]
            print("(a,b) -> ({},{})".format(a, b))
            new_a = a + status.age[move[1][0]]
            new_b = b + 1
            print("(new_a,new_b) -> ({},{})".format(new_a, new_b))
            score_.params[move[1][1]] = [new_a, new_b]
            if status.mage[move[1][1]] > 0:
                score_.total = score_.total + (abs(a / b - status.mage[move[1][1]]) if b > 0 else status.mage[move[1][1]]) - abs(new_a / new_b - status.mage[move[1][1]])
    elif move[0] == 'remove':
        '''
            ('remove', (participant i, event j))
        '''
        if status.age[move[1][0]] > 0:
            a, b = score_.params[move[1][1]]
            print("(a,b) -> ({},{})".format(a, b))
            new_a = a - status.age[move[1][0]]
            if b < 1:
                print("wtf {} {} {}".format(a, b, s[move[1][0]][move[1][1]]))
            new_b = b - 1 if b > 0 else 0 # FIXME shouldn't happen
            print("(new_a,new_b) -> ({},{})".format(new_a, new_b))
            score_.params[move[1][1]] = [new_a, new_b]
            if status.mage[move[1][1]] > 0:
                score_.total = score_.total + (abs(a / b - status.mage[move[1][1]]) if b > 0 else status.mage[move[1][1]]) - (abs(new_a / new_b - status.mage[move[1][1]]) if new_b > 0 else status.mage[move[1][1]])
    elif move[0] == 'move':
        print("x {} {}".format(score_.params[move[1][1]][0], score_.params[move[1][1]][1]))
        '''
            ('move', (participant i, event j1, event j2))
            -> ('remove', (i, j1)) + ('add', (i, j2))
        '''
        score_ = objective_median_age_incr(s, score_, ('remove', (move[1][0], move[1][1])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][1]] = 0
        score_ = objective_median_age_incr(s_, score_, ('add', (move[1][0], move[1][2])))
    elif move[0] == 'replace':
        '''
            ('replace', (participant i1, participant i2, event j))
            -> ('remove', (i1, j)) + ('add', (i2, j))
        '''
        score_ = objective_median_age_incr(s, score_, ('remove', (move[1][0], move[1][2])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        score_ = objective_median_age_incr(s_, score_, ('add', (move[1][1], move[1][2])))
    elif move[0] == 'swap':
        '''
            ('swap', (participant i1, participant i2, event j1, event j2))
            -> ('move', (i1, j1, j2)) + ('move', (i2, j2, j1))
        '''
        score_ = objective_median_age_incr(s, score_, ('move', (move[1][0], move[1][2], move[1][3])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        s_[move[1][0]][move[1][3]] = 1
        score_ = objective_median_age_incr(s_, score_, ('move', (move[1][1], move[1][3], move[1][2])))
    return score_

'''
    Sex ratio objective function.
    Defines the score (cost) of a given solution by its distance w.r.t. the sratio vector.
    input:
        _s: a solution
    output:
        the score of _s (Score object)
'''
def objective_sex_ratio(s):
    score = Score(objective_sex_ratio_incr)
    for j in range(len(s[0])):
        a, b = 0, 0
        for i in range(len(s)):
            a += (s[i][j] * status.male[i])
            b += s[i][j]
        score.params.append([a, b])
        if status.sratio[j] > 0:
            score.total -= abs(a / b - status.sratio[j]) if b > 0 else status.sratio[j]
    return score

'''
    Sex ratio objective function (incremental version).
    Defines the score of a given solution by its distance w.r.t. the sratio vector.
    input:
        _s: a solution
        _score: the score of _s (Score object)
        _move: a (operation_name, involved participants/events tuple) pair
    output:
        the score of _s after performing the move _move (Score object)
'''
def objective_sex_ratio_incr(s, score, move):
    score_ = Score(score.objective, score.total, score.params)
    print("{} : {}".format(score_.total, objective_sex_ratio(s).total))
    print(move)
    if move[0] == 'add':
        '''
            ('add', (participant i, event j))
        '''
        a, b = score_.params[move[1][1]]
        print("(a,b) -> ({},{})".format(a, b))
        new_a = a + status.male[move[1][0]]
        new_b = b + 1
        print("(new_a,new_b) -> ({},{})".format(new_a, new_b))
        score_.params[move[1][1]] = [new_a, new_b]
        if status.sratio[move[1][1]] > 0:
            score_.total = score_.total + (abs(a / b - status.sratio[move[1][1]]) if b > 0 else status.sratio[move[1][1]]) - abs(new_a / new_b - status.sratio[move[1][1]])
    elif move[0] == 'remove':
        '''
            ('remove', (participant i, event j))
        '''
        a, b = score_.params[move[1][1]]
        print("(a,b) -> ({},{})".format(a, b))
        new_a = a - status.male[move[1][0]]
        if b < 1:
            print("wtf {} {} {}".format(a, b, s[move[1][0]][move[1][1]]))
        new_b = b - 1 if b > 0 else 0 # FIXME shouldn't happen
        print("(new_a,new_b) -> ({},{})".format(new_a, new_b))
        score_.params[move[1][1]] = [new_a, new_b]
        if status.sratio[move[1][1]] > 0:
            score_.total = score_.total + (abs(a / b - status.sratio[move[1][1]]) if b > 0 else status.sratio[move[1][1]]) - (abs(new_a / new_b - status.sratio[move[1][1]]) if new_b > 0 else status.sratio[move[1][1]])
    elif move[0] == 'move':
        print("x {} {}".format(score_.params[move[1][1]][0], score_.params[move[1][1]][1]))
        '''
            ('move', (participant i, event j1, event j2))
            -> ('remove', (i, j1)) + ('add', (i, j2))
        '''
        score_ = objective_sex_ratio_incr(s, score_, ('remove', (move[1][0], move[1][1])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][1]] = 0
        score_ = objective_sex_ratio_incr(s_, score_, ('add', (move[1][0], move[1][2])))
    elif move[0] == 'replace':
        '''
            ('replace', (participant i1, participant i2, event j))
            -> ('remove', (i1, j)) + ('add', (i2, j))
        '''
        score_ = objective_sex_ratio_incr(s, score_, ('remove', (move[1][0], move[1][2])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        score_ = objective_sex_ratio_incr(s_, score_, ('add', (move[1][1], move[1][2])))
    elif move[0] == 'swap':
        '''
            ('swap', (participant i1, participant i2, event j1, event j2))
            -> ('move', (i1, j1, j2)) + ('move', (i2, j2, j1))
        '''
        score_ = objective_sex_ratio_incr(s, score_, ('move', (move[1][0], move[1][2], move[1][3])))
        s_ = [ss[:] for ss in s]
        s_[move[1][0]][move[1][2]] = 0
        s_[move[1][0]][move[1][3]] = 1
        score_ = objective_sex_ratio_incr(s_, score_, ('move', (move[1][1], move[1][3], move[1][2])))
    return score_

'''
    Selection function of the Best-Neighbor heuristic.
    Chooses the neighbor with the best evaluation (randomly).
    input:
        _s_legal: a list of (solution, move) pairs
    output:
        a pair among _s_legal for which the objective is maximum, uniformly randomly, paired with its score (Score object)
'''
def selection_best(s_legal):
    s_star = [s_legal[0]]
    s_star_score = status.objective(status.s_, status.s_score, s_legal[0][1])
    for s in s_legal:
        score = status.objective(status.s_, status.s_score, s[1])
        if score.total == s_star_score.total:
            s_star.append(s)
        elif score.total > s_star_score.total:
            s_star = [s]
            s_star_score = score
    return (s_star_score, s_star[random.randint(0, len(s_star) - 1)])

'''
    Selection function of the Best-K-Neighbors heuristic.
    Chooses randomly a neighbor among the best k.
    input:
        _s_legal: a list of (solution, move) pairs
    output:
        a pair among _s_legal for which the objective is among the status.k best
'''
def selection_best_k(s_legal):
    s_ = []
    for s in s_legal:
        score = status.objective(status.s_, status.s_score, s[1])
        s_.append((score, s))
    s = sorted(s_, key=lambda x: x[0].total, reverse=True)
    return s[random.randint(0, min(len(s) - 1, status.k - 1))]

'''
    Selection function of the First Improvement heuristic.
    Chooses the first neighbor improving the current solution objective.
    input:
        _s_legal: a list of (solution, move) pairs
    output:
        the first pair among _s_legal for which the objective outperfoms status.s_score, paired with its score (Score object)
        if none, the first pair ! FIXME: should return the best one in that case
'''
def selection_first_improvement(s_legal):
    s_star = s_legal[0]
    s_star_score = status.objective(status.s_, status.s_score, s_legal[0][1])
    for s in s_legal:
        score = status.objective(status.s_, status.s_score, s[1])
        if score.total > status.s_score.total:
            return (score, s)
    return (s_star_score, s_star)

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
def tabu_search(s, objective=objective_compound_incr, neighborhood=neighborhood_all, is_legal=is_legal_not_tabu, selection=selection_best):
    status.objective = objective
    status.s_star = s
    status.s_star_score = globals()[objective.__name__.replace('_incr', '')](status.s_star)
    status.s_ = status.s_star
    status.s_score = status.s_star_score
    tabu = []
    improving = status.improving
    while status.attempts and improving:
        s_legal = [s_neighbor for s_neighbor in neighborhood(status.s_) if is_legal(s_neighbor, tabu)]
        if len(s_legal) == 0: # optimum local; we should break - shouldn't happen anyway with improving and large n, m...
            expire_features(tabu, status.attempts)
            status.attempts -= 1
            continue
        status.s_score, s_ = selection(s_legal)
        status.s_, s_move = s_
        if status.s_score.total > status.s_star_score.total:
            if status.s_score.total - status.s_star_score.total >= status.delta:
                improving = status.improving + 1
            status.s_star = status.s_
            status.s_star_score = status.s_score
        for participant in extract_tabu_elements(s_move):
            tabu.append((status.attempts, participant))
        expire_features(tabu, status.attempts)
        status.attempts -= 1
        #improving -= 1
    return (status.s_star, status.s_star_score.total)

'''
    Performs a tabu search with restarts.
    input:
        _initial_solution: the function providing a feasible initial solution
        _objective: the objective function to maximize
        _neighborhood: the neighborhood generator function
        _is_legal: the legal moves filter function
        _selection: the selection function
    output:
        the best solution found after _restarts iterations and its score as a pair
'''
def tabu_search_restarts(initial_solution=initial_solution_top_down, objective=objective_friends_incr, neighborhood=neighborhood_all, is_legal=is_legal_not_tabu, selection=selection_best):
    s_star, s_star_score = None, 0
    while status.restarts:
        s_init = initial_solution(status.p, status.c, status.d)
        s, s_score = tabu_search(s_init, objective, neighborhood, is_legal, selection)
        if s_score > s_star_score:
            s_star_score = s_score
            s_star = s
        status.restarts -= 1
    return (s_star, s_star_score)
