#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This modules holds common project functions.
"""

# Imports #####################################################################
import logging
from datetime import timedelta

import arrow
import click

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "20-JUN-2017"
__license__ = "Proprietary"


# Globals #####################################################################
def print_log(message, nl=True, log_level=logging.DEBUG, force_print=False):
    ctx = click.get_current_context()

    if force_print or (not ctx.obj.quiet):
        click.echo(message, nl=nl)

    logging.log(log_level, message)


def format_future_time(minutes=0, seconds=0):
    return (
        (arrow.now().to("local") + timedelta(minutes=minutes, seconds=seconds))
        .strftime("%d-%b-%Y %I:%M %p %Z")
        .upper()
    )
