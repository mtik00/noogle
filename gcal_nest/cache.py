#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the cache for the gcal_nest application.
'''

# Imports #####################################################################
import sqlite3

from .settings import settings

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '05-JUN-2017'
__version__ = '1.0.0'


# Globals #####################################################################
CACHE = None


def get_cache():
    '''Return the application's Cache object.'''
    global CACHE  # pylint:disable=W0603
    if not CACHE:
        CACHE = Cache()

    return CACHE


class Cache(object):
    '''
    This object holds the application cache.
    '''

    def __init__(self):
        self.conn = sqlite3.connect('example.db')

    def history(self):
        '''
        Return a listing of historic event data.
        '''
        pass

    def do_event(self, event):
        '''
        Mark the event as completed.
        '''
        # Cache the current date/time, event name, etc
        pass
