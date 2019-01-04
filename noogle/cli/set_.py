#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module holds the cli `set` commands
"""

# Imports #####################################################################
import click
import arrow

from ..gcal import get_next_events
from ..nest import NestAPI
from ..helpers import print_log
from ..models import Action

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
    ctx = click.get_current_context().obj
    napi = NestAPI()
    napi.do_action(Action.home)


@set_.command()
def away():
    """Sets the structure to `away` and thermostat to `eco`"""
    ctx = click.get_current_context().obj
    napi = NestAPI()
    napi.do_action(Action.away)
