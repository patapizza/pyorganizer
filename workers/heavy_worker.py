#!/usr/bin/python

import math
import psycopg2
import time
import sys
from tabu_search import *

verbose = 1

def connect(params):
    con = None
    try:
        if verbose:
            print('--- Connecting...')
        con = psycopg2.connect(params)
        if verbose:
            print('--- Connected.')
    except psycopg2.DatabaseError as e:
        print('Error {}'.format(e))
    return con

def fetch_data(cur):
    if verbose:
        print('--- Fetching data...')
    cur.execute('SELECT * FROM users ORDER BY uid ASC')
    users = cur.fetchall()
    cur.execute('SELECT * FROM events WHERE decline_until>{} ORDER BY eid ASC'.format(time.time()))
    events = cur.fetchall()
    cur.execute('SELECT * FROM friends')
    friends = cur.fetchall()
    cur.execute('SELECT * FROM attendees')
    attendees = cur.fetchall()
    if verbose:
        print('...done!')
    return (users, events, friends, attendees)
    
def populate_data(users, events, friends, attendees):
    if verbose:
        print('--- Filling in status object...')

    '''initializing variables with default values'''
    n, m = len(users), len(events)
    p = [[0 for j in range(m)] for i in range(n)]
    c = [0 for j in range(m)]
    d = [[0 for j in range(m)] for i in range(m)]
    emax = [m] * n
    emin = [0] * n
    cf = [[0 for j in range(n)] for i in range(n)]
    age = [0] * n
    mage = [0] * m
    male = [0] * n
    sratio = [0] * m
    cmin = [0] * m
    chosen_ones = {}

    '''computing actual values of parameters'''
    uids = {}
    index = 0
    for user in users:
        uid, token, pic, min_events, max_events, username, birthday, gender = user
        uids[uid] = index
        emax[index] = max_events
        emin[index] = min_events
        age[index] = math.floor((time.time() - birthday) / (365.25 * 24 * 3600))
        male[index] = gender
        index += 1
    eids = {}
    index = 0
    for event in events:
        eid, name, pic, loc, starting, ending, capacity, owner, min_age, max_age, med_age, sex_ratio, subscribe_until, decline_until, min_capacity, open_, schedule_id = event
        eids[eid] = index
        c[index] = capacity
        mage[index] = med_age
        sratio[index] = sex_ratio
        cmin[index] = min_capacity
        index += 1
    for friend in friends:
        uid, fid = friend
        if fid in uids: # everyone doesn't use the app yet!
            cf[uids[uid]][uids[fid]] = 1
    participations = [0] * len(users)
    for attendee in attendees:
        eid, uid, status, pos, id_ = attendee
        if eid in eids and status == 1: # "attending"
            participations[uids[uid]] += 1
    for attendee in attendees:
        eid, uid, status, pos, id_ = attendee
        if eid in eids:
            if status == 1: # "attending"
                p[uids[uid]][eids[eid]] = (pos + participations[uids[uid]]) / participations[uids[uid]]
            if status == 3: # "chosen"
                chosen_ones[(uids[uid],eids[eid])] = 1
    for e1 in events:
        for e2 in events:
            if e1[4] <= e2[4] and e1[5] >= e2[4]:
                d[eids[e1[0]]][eids[e2[0]]] = 1

    '''populating variables with actual values'''
    status = Status(p, c, d)
    status.set_cf(cf)
    status.set_emin(emin)
    status.set_emax(emax)
    status.set_age(age)
    status.set_mage(mage)
    status.set_male(male)
    status.set_sratio(sratio)
    status.set_cmin(cmin)
    status.chosen_ones = chosen_ones

    if verbose:
        print('...done!')
    return status, uids, eids

def update_data(cur, uids, eids, s):
    for k, v in uids.items():
        for l, w in eids.items():
            status = 4
            if s[v][w] == 1:
                status = 3
            '''
                todo: check if user k didn't decline in the meanwhile
                if it's the case, run quick searches to check next participant
            '''
            cur.execute("UPDATE attendees SET status=%s WHERE status=1 AND uid=%s AND eid=%s", (status, k, l))

if __name__ == "__main__":
    params = "dbname=db host=localhost port=5432 user=foo password=bar"

    '''connecting'''
    con = connect(params)
    if not con:
        sys.exit(1)
    cur = con.cursor()
    
    '''fetching data from db'''
    users, events, friends, attendees = fetch_data(cur)

    '''closing connection'''
    con.close()

    '''initializing status object'''
    status, uids, eids = populate_data(users, events, friends, attendees)

    print("Preferences matrix: {}".format(status.p))
    print("Exclusion matrix: {}".format(status.d))
    print("CF adjacency matrix: {}".format(status.cf))
    print("Capacity vector: {}".format(status.c))
    print("Emax: {}".format(status.emax))

    '''setting meta-parameters'''
    status.attempts = 100
    status.tenure = 0
    status.improving = 5
    status.delta = 0
    status.allowed_time = 60
    status.set_status()

    '''launching search'''
    init = initial_solution_top_down(status.p, status.c, status.d)
    s, score = tabu_search(init, objective_compound_incr, neighborhood_all, is_legal_not_tabu, selection_best_k)
    print("Solution score: {}".format(score))
    print("Solution: {}".format(s))

    '''connecting'''
    con = connect(params)
    if not con:
        sys.exit(1)
    cur = con.cursor()
    
    '''updating database'''
    if verbose:
        print("--- Updating database...")
    update_data(cur, uids, eids, s)
    con.commit()
    if verbose:
        print("...done.")

    '''closing connection'''
    con.close()
