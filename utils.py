#!/usr/bin/env python

def from_military_time(x):
    suffix = ':00am' if x < 12 else ':00pm'
    return str(x % 12) + suffix
