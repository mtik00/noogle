#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
"""
This module holds the cli `main` command
"""

# Imports #####################################################################
import click

from ..gcal import get_next_gcal_events
from ..helpers import print_log

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUN-2017"
__license__ = "Proprietary"


# Globals #####################################################################
@click.command()
def go():
    """
    Main function to get and process events.
    """
    ctx = click.get_current_context().obj

    # get new events
    # put them in cache, if they aren't there already
    # see if we need to do anything
    # do it!
    # click.clear()
    # ctx.logger.fatal("doh!")

    # Grab the next 10 events
    print_log("Reading events from Google calendar...", nl=False)
    q_filter = "nestd" if ctx.debug else "nest"
    my_events = get_next_gcal_events(max_results=10, q_filter=q_filter)
    print_log("...done")

    ctx.cache.add_if_not_exists(ctx, my_events)

    for event in my_events:
        if not ctx.cache.exists(event.event_id):
            print_log("caching new event: {0}".format(event))
            ctx.cache.add_event(event)

    # Get all events that haven't been actioned
    my_events = [x for x in ctx.cache.waiting()]
    print_log(my_events)
