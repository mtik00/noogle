#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
This module holds the cli `service` commands
'''

# Imports #####################################################################
import sys
import time
from random import SystemRandom as random

import click
import arrow

from ..gcal import get_next_events
from ..helpers import format_future_time, print_log


# Globals #####################################################################
@click.group()
def service():
    '''Run a command in service mode'''
    pass


@service.command()
def gcal(minutes=5):
    '''Look for events in Google and add them to the cache'''
    ctx = click.get_current_context().obj

    while True:
        # Grab the next 10 events
        print_log('Reading events from Google calendar...', nl=False)
        q_filter = 'nestd' if ctx.debug else 'nest'
        my_events = get_next_events(max_results=10, q_filter=q_filter)
        print_log('...done')

        for event in my_events:
            if not ctx.cache.exists(event.event_id):
                print_log("caching new event: {0}".format(event))
                ctx.cache.add_event(event)

        print_log('waiting until %s' % format_future_time(minutes))
        time.sleep(minutes * 60)


@service.command()
def nest(minutes=5):
    '''Wait for and process Nest events'''
    ctx = click.get_current_context().obj

    while True:
        events = ctx.cache.waiting()

        # Look for any events that are past, but within 2 days.
        two_days_ago = arrow.get(days=-2)
        events = [event for event in events if arrow.get(event.scheduled_date) <= two_days_ago]

        if events:
            print_log('%d events waiting...' % len(events), nl=False)

        for event in events:
            print_log('...doing %s' % event)
            ctx.cache.do_event(event)
            print_log('......done')

        print_log('waiting until %s' % format_future_time(minutes))
        time.sleep(minutes * 60)
