#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the Event class.
'''

# Imports #####################################################################
import enum
import arrow

from .settings import get_settings

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '07-JUN-2017'


# Globals #####################################################################
class State(enum.Enum):
    waiting = 0
    complete = 1
    removed = 2

    def __str__(self):
        return self.name


class Action(enum.Enum):
    home = 0
    away = 1


class Event(object):
    '''Describes a single event stored in cache.'''
    def __init__(self, db_dict=None, gcal_event=None, timezone=None):
        self.name = None
        self.action = None
        self.event_id = None
        self.calendar_id = 'primary'
        self.parent_event_id = None  # Not currently used
        self.state = State.waiting
        self.scheduled_date = None
        self.actioned_date = None
        self.timezone = None
        self.description = None

        if db_dict:
            self.from_db(db_dict)
        elif (gcal_event and timezone):
            self.from_gcal_dict(gcal_event, timezone)

    def __str__(self):
        return "{0}: {1}".format(
            arrow.get(self.scheduled_date).format('YYYY-MM-DD HH:mm'),
            self.name,
        )

    def waiting(self):
        return self.state == State.waiting

    def from_db(self, db_dict):
        '''Initialize this object from a db row dict.'''
        self.name = db_dict['name']
        self.action = db_dict['action']
        self.event_id = db_dict['event_id']
        self.calendar_id = db_dict['calendar_id']
        self.parent_event_id = db_dict['parent_event_id']
        self.state = State(db_dict['state'])
        self.scheduled_date = arrow.get(db_dict['scheduled_date']).to(db_dict['timezone'])
        self.actioned_date = arrow.get(db_dict['actioned_date']).to(db_dict['timezone'])
        self.timezone = db_dict['timezone']
        self.description = db_dict['description']

    def from_gcal_dict(self, event, timezone):
        '''Initialize this object from a google calendar dict'''
        default_start_time = get_settings().get('calendar.default-start-time')

        self.name = event['summary']
        self.event_id = event['id']
        self.parent_event_id = None

        if 'date' in event['start']:
            self.scheduled_date = arrow.get(event['start']['date'] + ' ' + default_start_time + ' ' + timezone, 'YYYY-MM-DD H:mm ZZZ')
        else:
            # NOTE: 'dateTime' includes the timezone
            self.scheduled_date = arrow.get(event['start'].get('dateTime'))
        self.actioned_date = None
        self.timezone = timezone

        parts = self.name.split(':')
        if len(parts) == 2:
            self.action = Action[parts[1]]
        elif len(parts) == 3:
            self.action = Action[parts[1]]
            self.description = parts[2]
        else:
            print(f'WARNING: Cannot parse event name: "{self.name}"')
