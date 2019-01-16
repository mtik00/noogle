#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
This module holds the cli `set` commands
"""

# Imports #####################################################################
import click
import arrow

from ..helpers import print_log
from ..nest import NestAPI
from ..models import Action, Event, State

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUN-2017"
__license__ = "MIT"


# Globals #####################################################################
@click.group(name="set")
def set_():
    """Set parameters"""
    ctx = click.get_current_context()

    # No reason to continue if we're in quiet mode
    if ctx.obj.quiet:
        ctx.exit()


@set_.command()
def home():
    """Sets the structure to `home` and thermostat to `heat`"""
    napi = NestAPI()
    napi.do_action(Action.home)


@set_.command()
def away():
    """Sets the structure to `away` and thermostat to `eco`"""
    napi = NestAPI()
    napi.do_action(Action.away)


def print_event(index, event):
    if index is None:
        print_log(
            "{:<19s}({:^9}) {}".format(
                event.scheduled_date.to("local").format("YYYY-MM-DD h:mmA"),
                event.state,
                event.name,
            )
        )
    else:
        print_log(
            "{:3})  {:<19s}({:^9}) {}".format(
                index + 1,
                event.scheduled_date.to("local").format("YYYY-MM-DD h:mmA"),
                event.state,
                event.name,
            )
        )


@set_.command()
def events():
    """Sets the states of cached events"""
    ctx = click.get_current_context().obj

    lookback = ctx.project_settings.get("calendar.lookback") or 0

    since = arrow.now().replace(
        days=-1 * lookback, hour=0, minute=0, second=0, microsecond=0
    )

    click.clear()
    print_log("Showing events since %s" % since.to("local").strftime("%A, %d %B"))

    states_str = ", ".join(
        ["{} for {}".format(state.value, state.name) for state in State]
    )
    state_values = [state.value for state in State]

    while True:
        events = [
            e for e in ctx.session.query(Event).filter(Event.scheduled_date >= since)
        ]

        for index, event in enumerate(events):
            print_event(index, event)

        value = input("Which event would you like to change (q to quit): ")
        if value.lower().startswith("q"):
            return
        elif not value.isdigit():
            print(f"ERROR: Invalid value '{value}'.  Please try again")
            continue

        value = int(value)

        if not (1 <= value <= len(events)):
            print(f"ERROR: Invalid value '{value}'.  Please try again")
            continue

        event = events[value - 1]

        print("*" * 40)
        print_event(index=None, event=event)
        print()
        value = input(f"Enter {states_str}: ")

        if not value.isdigit():
            print(f"ERROR: Invalid value '{value}'.  Please try again")
            continue

        value = int(value)

        if value not in state_values:
            print(f"ERROR: Invalid value '{value}'.  Please try again")
            continue

        event.state = State(value).name
        ctx.session.add(event)
        ctx.session.commit()
