#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the main interface for the gcal_nest package.
'''

# Imports #####################################################################
# from .settings import get_object as get_settings_object
# from .logger import get_logger
import logging

import click

from .gcal import get_next_events
from .helpers import print_log


# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '08-JUN-2017'
__version__ = '1.0.0b1'


# Globals #####################################################################
def main(ctx):
    '''
    Main function to get and process events.
    '''
    # get new events
    # put them in cache, if they aren't there already
    # see if we need to do anything
    # do it!
    # click.clear()
    # ctx.logger.fatal("doh!")

    # Grab the next 10 events
    print_log(ctx, 'Reading events from Google calendar...', nl=False)
    my_events = get_next_events(max_results=10)
    print_log(ctx, '...done')

    ctx.cache.add_if_not_exists(ctx, my_events)

    # for event in my_events:
    #     if not ctx.cache.exists(event.event_id):
    #         print_log(ctx, "caching new event: {0}".format(event))
    #         ctx.cache.add_event(event)

    # Get all events that haven't been actioned
    my_events = [x for x in ctx.cache.waiting()]
    print_log(ctx, my_events)
