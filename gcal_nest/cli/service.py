#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module holds the cli `service` commands
"""

# Imports #####################################################################
import sys
import time
import traceback
from random import SystemRandom as random

import click
import arrow
import inflect
from sqlalchemy import and_

from ..gcal import get_next_events
from ..nest import do_event
from ..helpers import format_future_time, print_log
from ..mailgun import send_message
from ..models import Event, State
from ..db import session

# Globals #####################################################################
inflect_engine = inflect.engine()


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
        gcal_events = get_next_events(max_results=10, q_filter=q_filter)
        print_log("GCAL: ...done")

        for event in gcal_events:
            if not Event.exists(event["id"]):
                message = f"GCAL: caching new event: {event}"
                print_log(message)
                text_lines.append(message)
                Event.create_from_gcal(event)

        # Any event that's not completed and not found in our list should be
        # set to 'removed'.
        gcal_ids = [x["id"] for x in gcal_events]
        waiting_events = Event.waiting()
        removed_events = (
            session.query(Event)
            .filter(
                and_(
                    Event.event_id.notin_([x["id"] for x in gcal_events]),
                    Event.state == State.waiting,
                )
            )
            .all()
        )
        if removed_events:
            print_log(
                "found {} cached {} that aren't in gcal".format(
                    len(removed_events),
                    inflect_engine.plural("event", len(removed_events)),
                )
            )

        for event in removed_events:
            message = f"GCAL: marking missing event: {event}"
            text_lines.append(message)
            print_log(message)
            event.mark_event_missing()

        # Send the email
        if text_lines:
            print_log("sending message")
            send_message(
                subject="New {} scheduled".format(
                    inflect_engine.plural("event", len(text_lines))
                ),
                text="\n".join(text_lines),
            )
            text_lines = []

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
        events = Event.waiting()

        # Look for any events that are past, but within 2 days.
        two_days_ago = arrow.get().shift(days=-2)
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

            try:
                do_event(ctx, event)
                event.mark_event_done(event)
            except Exception as e:
                text_lines.append(str(e))
                text_lines.append(traceback.format_exc())

            print_log("NEST: ......done")

        if text_lines:
            print_log("sending message")
            send_message(
                subject="New {} processed".format(
                    inflect_engine.plural("event", len(text_lines))
                ),
                text="\n".join(text_lines),
            )
            text_lines = []

        print_log("NEST: waiting until %s" % format_future_time(seconds=poll))
        time.sleep(poll)
