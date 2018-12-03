#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module holds the cli `service` commands
"""

# Imports #####################################################################
import sys
import time
from random import SystemRandom as random

import click
import arrow
import inflect

from ..gcal import get_next_events
from ..helpers import format_future_time, print_log
from ..mailgun import send_message


# Globals #####################################################################
engine = inflect.engine()


@click.group()
def service():
    """Run a command in service mode"""
    pass


@service.command()
@click.option("-p", "--poll", default=5)
def gcal(poll):
    """Look for events in Google and add them to the cache"""
    ctx = click.get_current_context().obj
    poll *= 60
    text_lines = []

    while True:
        # Grab the next 10 events
        print_log("GCAL: Reading events from Google calendar...")
        q_filter = "nest"
        my_events = get_next_events(max_results=10, q_filter=q_filter)
        print_log("GCAL: ...done")

        for event in my_events:
            if not ctx.cache.exists(event.event_id):
                message = f"GCAL: caching new event: {event}"
                print_log(message)
                ctx.cache.add_event(event)
                text_lines.append(message)

        if text_lines:
            print_log("sending message")
            send_message(
                subject="New {} scheduled".format(
                    engine.plural("event", len(text_lines))
                ),
                text="\n".join(text_lines),
            )
            text_lines = []

        # Any event that's not completed and not found in our list should be
        # set to 'removed'.

        print_log("GCAL: waiting until %s" % format_future_time(seconds=poll))
        time.sleep(poll)


@service.command()
@click.option("-p", "--poll", default=5)
def nest(poll=5):
    """Wait for and process Nest events"""
    ctx = click.get_current_context().obj
    poll *= 60
    text_lines = []

    while True:
        events = ctx.cache.waiting()

        # Look for any events that are past, but within 2 days.
        two_days_ago = arrow.get(days=-2)
        events = [
            event
            for event in events
            if (arrow.get(event.scheduled_date) >= two_days_ago)
            and (arrow.get(event.scheduled_date) <= arrow.now())
        ]

        if events:
            print_log("NEST: %d events waiting..." % len(events), nl=False)

        for event in events:
            text_lines.append(f"NEST:...doing {event}")
            print_log(f"NEST:...doing {event}")
            ctx.cache.do_event(event)
            print_log("NEST: ......done")

        if text_lines:
            print_log("sending message")
            send_message(
                subject="New {} processed".format(
                    engine.plural("event", len(text_lines))
                ),
                text="\n".join(text_lines),
            )
            text_lines = []

        print_log("NEST: waiting until %s" % format_future_time(seconds=poll))
        time.sleep(poll)
