#!/usr/bin/env python

def from_military_time(military):
    suffix = ':00am' if military < 12 else ':00pm'
    standard = 12 if military % 12 == 0 else military % 12
    return str(standard) + suffix
