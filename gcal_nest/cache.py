#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the cache for the gcal_nest application.
'''

# Imports #####################################################################
import os
import sqlite3
from contextlib import contextmanager

import arrow

from .settings import USER_FOLDER
from .event import Event

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '05-JUN-2017'


# Globals #####################################################################
CACHE = None
DB_INIT = '''
CREATE TABLE IF NOT EXISTS events (
    id integer PRIMARY KEY,
    name text NOT NULL,
    event_id integer NOT NULL UNIQUE,
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
        self._columns = []

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass

    @property
    def columns(self):
        if self._columns:
            return self._columns

        cursor = self.conn.execute('select * from events')
        self._columns = [description[0] for description in cursor.description]
        return self._columns

    def exists(self, event_id):
        '''
        Checks the specified `event_id` and returns True if its in the cache.
        '''
        self.cursor.execute("SELECT count(*) FROM events WHERE event_id = ?", (event_id,))
        data = self.cursor.fetchone()[0]
        return data != 0

    def waiting(self):
        '''
        Return all events from the cache that are waiting to be completed.
        '''
        self.cursor.execute("SELECT * FROM events WHERE state = ?", ('WAITING',))
        data = self.cursor.fetchall()
        events = [
            Event(
                db_dict=dict(zip(self.columns, x))
            ) for x in data]

        return sorted(events, key=lambda x: x.scheduled_date)

    def do_event(self, event, commit=True):
        '''
        Mark the event as completed.
        '''
        if isinstance(event, basestring):
            event_id = event
        else:
            event_id = event.event_id

        self.cursor.execute(
            """UPDATE events SET state = ? WHERE event_id = ? """,
            ('COMPLETE', event_id)
        )

        if commit:
            self.conn.commit()

    def get_event(self, event_id):
        '''
        Returns the specified event, if it exists.
        '''
        self.cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
        data = self.cursor.fetchone()

        if data:
            return Event(
                db_dict=dict(zip(self.columns, data))
            )

        return None

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
                str(event.scheduled_date),
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
    e.scheduled_date = arrow.now()
    cache.add_event(e)


if __name__ == '__main__':
    main()
