#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
"""
This module holds the cli `show` commands
"""

import arrow

# Imports #####################################################################
import click

from ..helpers import print_log
from ..models import Event, State
from ..nest import NestAPI

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUN-2017"
__license__ = "Proprietary"


# Globals #####################################################################
@click.group()
def show():
    """Show information"""
    ctx = click.get_current_context()

    # No reason to continue if we're in quiet mode
    if ctx.obj.quiet:
        ctx.exit()


@show.command()
@click.option("--max-events", default=10, help="maximum number of events to show")
@click.option(
    "--removed/--no-removed",
    default=False,
    help="show removed events too (default is --no-removed)",
)
def events(max_events, removed):
    """Display the next events from Google calendar"""
    ctx = click.get_current_context().obj

    lookback = ctx.project_settings.get("calendar.lookback") or 0
    since = (
        arrow.now()
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .shift(days=-1 * lookback)
    )

    print_log("Showing events since %s" % since.to("local").strftime("%A, %d %B"))

    events = ctx.session.query(Event).filter(Event.scheduled_date >= since)

    if not removed:
        events = events.filter(Event.state != State.removed)

    if not events.count():
        print_log("--- no events found")
        return

    timezone = ctx.project_settings.get("calendar.timezone", "UTC")
    for event in events.order_by(Event.scheduled_date):
        print_log(
            "{:<20s}({:^9}) {}".format(
                event.scheduled_date.to(timezone).format("YYYY-MM-DD hh:mm A"),
                event.state,
                event.name,
            )
        )


@show.command()
def cache():
    """
    Shows the cached events
    """
    ctx = click.get_current_context().obj

    # For the pager to work, we need to create one big string.
    str_events = []
    for event in ctx.session.query(Event).all():
        str_events.append(
            "{:<19s}({:^9}) {}".format(
                event.scheduled_date.format("YYYY-MM-DD h:mmA"), event.state, event.name
            )
        )

    click.echo_via_pager("\n".join(str_events))


@show.command()
def structures():
    """Show the structure information"""
    NestAPI().show()


@show.command()
def away():
    """Show the away state for the controlled thermostat"""
    ctx = click.get_current_context().obj
    napi = NestAPI()

    structure_name = ctx.project_settings.get("nest.structure")
    structure = next((x for x in napi.structures if x.name == structure_name))

    print_log("Structure: %s" % structure.name)
    print_log("     Away: %s" % structure.away)
