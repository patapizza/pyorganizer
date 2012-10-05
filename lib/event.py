#!/usr/bin/env python3

class Event:

    ''' constructor
    inputs
        name: the event's name
    startdate: a datetime.datetime object representing the starting date of the event
    enddate: a datetime.datetime object representing the ending date of the event
    capacity: the event's capacity (0: infinite)
    '''
    def __initialize__(self, name, startdate, enddate, capacity):
    self.name = name
        self.startdate = startdate
        self.enddate = enddate
    self.capacity = capacity

    def get_capacity(self):
        return self.capacity

    def get_date(self):
        return self.date

    def get_name(self):
        return self.name 
