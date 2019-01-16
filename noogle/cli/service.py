#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module holds the cli `service` commands
"""

import time
import traceback
from pprint import pformat

import arrow
import click
import inflect
from sqlalchemy import and_

from ..db import session
from ..gcal import get_next_events
from ..helpers import format_future_time, print_log
from ..logger import clear_logger, get_logger
from ..mailgun import send_message
from ..models import Event, State
from ..nest import NestAPI
from ..settings import DEBUG, DEPLOY_SETTINGS, get_settings
from ..utils import absjoin, get_scheduled_date

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

    if get_settings().get("general.use-logfile"):
        logpath = absjoin(DEPLOY_SETTINGS.get("app_log_dir"), "gcal.log")

        clear_logger()
        ctx.logger = get_logger(logfile_path=logpath)

    while True:
        # Grab the next 10 events
        print_log("GCAL: Reading events from Google calendar...")
        q_filter = "nest"
        gcal_events = get_next_events(max_results=10, q_filter=q_filter)
        print_log("GCAL: ...done")

        for event in gcal_events:
            if not Event.exists(
                event["id"], get_scheduled_date(event), state=State.waiting
            ):
                existing = (
                    session.query(Event)
                    .filter(
                        and_(
                            Event.event_id == event["id"],
                            Event.scheduled_date == get_scheduled_date(event),
                        )
                    )
                    .first()
                )

                if existing and (existing.state != State.waiting):
                    # The event has already been completed
                    continue

                message = f"GCAL: caching new event:\n" + pformat(event)
                print_log(message)
                text_lines.append(message)
                Event.create_from_gcal(event)

        # Any event that's not completed and not found in our list should be
        # set to 'removed'.
        removed_events = Event.events_missing(gcal_events)

        if removed_events:
            print_log(
                "found {} cached {} that aren't in gcal".format(
                    len(removed_events),
                    inflect_engine.plural("event", len(removed_events)),
                )
            )

        for event in removed_events:
            message = f"GCAL: marking missing event:\n" + pformat(repr(event))
            text_lines.append(message)
            print_log(message)
            event.mark_event_missing()

        # Send the email
        if DEBUG and text_lines:
            print_log("DEBUG on; would have sent:")
            print_log("\n".join(text_lines))
        elif text_lines:
            print_log("sending message")
            send_message(
                subject="{} processed".format(
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
    api = None

    if get_settings().get("general.use-logfile"):
        logpath = absjoin(DEPLOY_SETTINGS.get("app_log_dir"), "nest.log")

        clear_logger()
        ctx.logger = get_logger(logfile_path=logpath)

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
            api = NestAPI()

        for event in events:
            text_lines.append(f"NEST:...doing {event}")
            print_log(f"NEST:...doing {event}")

            try:
                api.do_action(event.action)
                event.mark_event_done()
                text_lines.append("NEST: ......done")
            except Exception as e:
                text_lines.append(str(e))
                text_lines.append(traceback.format_exc())

            print_log("NEST: ......done")

        # Send the email
        if DEBUG and text_lines:
            print_log("DEBUG on; would have sent:")
            print_log("\n".join(text_lines))
        elif text_lines:
            print_log("sending message")
            send_message(
                subject="{} processed".format(
                    inflect_engine.plural("Event", len(text_lines))
                ),
                text="\n".join(text_lines),
            )
            text_lines = []

        print_log("NEST: waiting until %s" % format_future_time(seconds=poll))
        time.sleep(poll)
