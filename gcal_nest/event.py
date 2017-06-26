#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the Event class.
'''

# Imports #####################################################################
import arrow

from .settings import get_settings

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '07-JUN-2017'


# Globals #####################################################################
STATES = ['WAITING', 'COMPLETE']


class Event(object):
    '''Describes a single event stored in cache.'''
    def __init__(self, db_dict=None, gcal_event=None, timezone=None):
        self.name = None
        self.event_id = None
        self.calendar_id = 'primary'
        self.parent_event_id = None
        self.state = 'WAITING'
        self.scheduled_date = None
        self.actioned_date = None
        self.timezone = None

        if db_dict:
            self.from_db(db_dict)
        elif (gcal_event and timezone):
            self.from_gcal_dict(gcal_event, timezone)

    def __str__(self):
        return "{0}: {1}".format(
            arrow.get(self.scheduled_date).format('YYYY-MM-DD HH:mmA'),
            self.name,
        )

    def waiting(self):
        return str(self.state).lower() == 'waiting'

    def from_db(self, db_dict):
        '''Initialize this object from a db row dict.'''
        self.name = db_dict['name']
        self.event_id = db_dict['event_id']
        self.calendar_id = db_dict['calendar_id']
        self.parent_event_id = db_dict['parent_event_id']
        self.state = db_dict['state']
        self.scheduled_date = arrow.get(db_dict['scheduled_date']).to(db_dict['timezone'])
        self.actioned_date = arrow.get(db_dict['actioned_date']).to(db_dict['timezone'])
        self.timezone = db_dict['timezone']

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
