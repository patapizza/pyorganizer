#!/usr/bin/python

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
        if eid in eids and (status == 1 or status == 3 or status == 4): # "subscribed" or "confirmed" or "not chosen"
            participations[uids[uid]] += 1
    declines = []
    for attendee in attendees:
        eid, uid, status, pos, id_ = attendee
        if eid in eids:
            if status == 1 or status == 3 or status == 4: # "subscribed" or "confirmed" or "not chosen"
                p[uids[uid]][eids[eid]] = (pos + participations[uids[uid]]) / participations[uids[uid]]
            if status == 3: # "confirmed"
                chosen_ones[(uids[uid],eids[eid])] = 1
            if status == 5: # "declined"
                declines.append((uid, eid))
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
    return status, uids, eids, declines

def update_data(cur, uids, eids, declines, s):
    for k, v in uids.items():
        for l, w in eids.items():
            if (k, l) in declines:
                cur.execute("DELETE FROM attendees WHERE status=5 AND uid=%s AND eid=%s", (k, l))
            else:
                cur.execute("UPDATE attendees SET status=%s WHERE status=1 AND uid=%s AND eid=%s", ((3 if s[v][w] == 1 else 4), k, l))

'''
    Checks if any user declined during previous (heavy) search.
    If so, we need to relaunch a (light) search.
'''
def check_declines(cur):
    cur.execute("SELECT * FROM attendees WHERE status=5")
    return 1 if len(cur.fetchall()) > 0 else 0

if __name__ == "__main__":
    params = "dbname=dauascre1055ft host=ec2-54-243-129-149.compute-1.amazonaws.com port=5432 user=socxkxdtrjhzld password=NxE_6PoOnApdQO5758kyPPuSot sslmode=require"
    #params = "dbname=eorganizer host=localhost port=5432 user=eorganizer password=30rg4n1z3r"
    #params = "dbname=db host=localhost port=5432 user=foo password=bar"

    declines = 1
    while declines:
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
        status, uids, eids, declines = populate_data(users, events, friends, attendees)

        print("Preferences matrix: {}".format(status.p))
        print("Exclusion matrix: {}".format(status.d))
        print("CF adjacency matrix: {}".format(status.cf))
        print("Capacity vector: {}".format(status.c))
        print("Emax: {}".format(status.emax))

        '''setting meta-parameters'''
        status.attempts = 100
        status.tenure = 1
        status.improving = 5
        status.delta = 2
        status.allowed_time = 60
        status.set_status()

        '''launching search'''
        if verbose:
            print("Launching {} search... ({} seconds)".format(("light" if len(declines) > 0 else "heavy"), status.allowed_time))
        init = initial_solution_bottom_up(status.p, status.c, status.d)
        neighborhood = neighborhood_all
        if len(declines) > 0:
            neighborhood = neighborhood_add
            status.attempts = len(declines) * len(events)
            status.tenure = 0
            init = initial_solution_confirmed_only()
        s, score = tabu_search(init, objective_compound_incr, neighborhood, is_legal_not_tabu, selection_best_k)
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
        update_data(cur, uids, eids, declines, s)
        con.commit()
        if verbose:
            print("...done.")

        '''checking if we need to launch a "light" search'''
        declines = check_declines(cur)

        '''closing connection'''
        con.close()
