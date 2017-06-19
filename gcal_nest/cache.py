#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the cache for the gcal_nest application.
'''

# Imports #####################################################################
import os
import sqlite3
from contextlib import contextmanager

from .settings import USER_FOLDER

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '05-JUN-2017'


# Globals #####################################################################
CACHE = None
DB_INIT = '''
CREATE TABLE IF NOT EXISTS events (
    id integer PRIMARY KEY,
    name text NOT NULL,
    event_id integer NOT NULL,
    calendar_id text NOT NULL,
    parent_event_id integer,
    state integer,
    scheduled_date text NOT NULL,
    actioned_date text
);
'''


def get_cache():
    '''Return the application's Cache object.'''
    global CACHE  # pylint:disable=W0603
    if not CACHE:
        CACHE = Cache()

    return CACHE


class Event(object):
    '''Describes a single event stored in cache.'''
    def __init__(self):
        self.name = None
        self.event_id = None
        self.calendar_id = None
        self.parent_event_id = None
        self.state = None
        self.scheduled_date = None
        self.actioned_date = None

    def from_db(self, db_tuple):
        '''Initialize this object from a db row / tuple.'''
        (
            _, self.name, self.event_id, self.calendar_id,
            self.parent_event_id, self.state, self.scheduled_date,
            self.actioned_date) = db_tuple


class Cache(object):
    '''
    This object holds the application cache.
    '''

    insert_sql = '''
            INSERT INTO events(name,event_id,calendar_id,parent_event_id,
            state,scheduled_date,actioned_date)
            VALUES(?,?,?,?,?,?,?)
    '''

    def __init__(self, path=None):
        if not os.path.isdir(USER_FOLDER):
            os.makedirs(USER_FOLDER)

        self.default_path = os.path.join(USER_FOLDER, 'gcal_nest.db')
        self.conn = sqlite3.connect(path or self.default_path)
        self.cursor = self.conn.cursor()

    def __del__(self):
        if self.conn:
            self.conn.close()

    @contextmanager
    def committed(self):
        '''Yields an auto-commited cache object'''
        yield self
        self.conn.commit()

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

    def add(self, item, commit=True):
        '''
        Add a single item to the cache.
        '''
        if isinstance(item, Event):
            return self.add_event(item, commit)

        self.conn.execute(Cache.insert_sql, item)

        if commit:
            self.conn.commit()

    def add_event(self, event, commit=True):
        '''
        Add a single event to the cache.
        '''
        self.conn.execute(
            Cache.insert_sql,
            tuple([
                event.name,
                event.event_id,
                event.calendar_id,
                event.parent_event_id,
                event.state,
                event.scheduled_date,
                event.actioned_date
            ])
        )

        if commit:
            self.conn.commit()


def main():
    cache = Cache()
    cache.cursor.execute('DROP TABLE IF EXISTS events;')
    cache.cursor.execute(DB_INIT)

    e = Event()
    e.name = "nest:50"
    e.event_id = 1
    e.calendar_id = "primary"
    e.scheduled_date = "today!"
    cache.add(e)

    # with cache.committed() as c:
    #     c.add(e)


if __name__ == '__main__':
    main()
