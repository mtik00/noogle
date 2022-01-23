#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
This module holds the cli `set` commands
"""

import arrow
import click

from ..helpers import print_log
from ..models import Action, Event, State
from ..nest import NestAPI
from ..settings import settings

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

    lookback = settings.calendar.lookback

    since = (
        arrow.now()
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .shift(days=-1 * lookback)
    )

    click.clear()
    print_log("Showing events since %s" % since.to("local").strftime("%A, %d %B"))

    states = ["{} for {}".format(state.value, state.name) for state in State]

    state_values = [state.value for state in State]

    while True:
        events = [
            e for e in ctx.session.query(Event).filter(Event.scheduled_date >= since)
        ]

        for index, event in enumerate(events):
            print_event(index, event)

        choices = [str(x) for x in range(0, len(events) + 1)]
        value = click.prompt(
            "Which event would you like to change (0 to quit)",
            type=click.Choice(choices),
            value_proc=lambda x: int(x),
            show_choices=True,
        )

        if value == 0:
            return
        elif not (1 <= value <= len(events)):
            print_log(f"ERROR: Invalid value '{value}'.  Please try again")
            continue

        event = events[value - 1]

        print_log("*" * 40)
        print_event(index=None, event=event)
        print_log()

        value = click.prompt(
            "Enter",
            type=click.Choice(states),
            value_proc=lambda x: int(x),
            show_choices=True,
        )

        if value not in state_values:
            print_log(f"ERROR: Invalid value '{value}'.  Please try again")
            continue

        event.state = State(value).name
        ctx.session.add(event)
        ctx.session.commit()
