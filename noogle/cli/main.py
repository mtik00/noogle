#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module holds the cli `main` command
"""

# Imports #####################################################################
import click

from ..gcal import get_next_gcal_events
from ..helpers import print_log
from ..models import Event

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

    # Grab the next 10 events
    print_log("Reading events from Google calendar...", nl=False)
    q_filter = "nestd" if ctx.debug else "nest"
    my_events = get_next_gcal_events(max_results=10, q_filter=q_filter)
    print_log("...done")

    my_events = [Event.create_from_gcal(x, commit=False) for x in my_events]

    for event in my_events:
        if not Event.exists(event.event_id, event.scheduled_date):
            print_log("caching new event: {0}".format(event))
            event.commit()

    # Get all events that haven't been actioned
    waiting_events = Event.waiting()
    print_log(waiting_events)
