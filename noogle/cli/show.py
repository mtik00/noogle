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

# Imports #####################################################################
import click
import arrow

from ..gcal import get_next_events
from ..nest import NestAPI
from ..helpers import print_log
from ..models import Event

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
def events(max_events):
    """Display the next events from Google calendar"""
    ctx = click.get_current_context().obj

    q = "nest"
    if ctx.debug:
        q = "nestd"

    lookback = ctx.project_settings.get("calendar.lookback") or 0

    since = arrow.now().replace(
        days=-1 * lookback, hour=0, minute=0, second=0, microsecond=0
    )

    print_log("Showing events since %s" % since.strftime("%A, %d %B"))

    for event in ctx.session.query(Event).filter(Event.scheduled_date >= since):
        print_log(
            "{:<19s}({:^9}) {}".format(
                event.scheduled_date.format("YYYY-MM-DD h:mmA"), event.state, event.name
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

    print("Structure: %s" % structure.name)
    print("     Away: %s" % structure.away)
