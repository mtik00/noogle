#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module holds the cli `clear` commands
"""

import logging

import click

from ..gcal import purge_db as gcal_purge_db
from ..nest import purge_db as nest_purge_db


@click.group(name="purge")
def purge():
    """Purge data from the database"""
    ctx = click.get_current_context()

    # No reason to continue if we're in quiet mode
    if ctx.obj.quiet:
        ctx.exit()


@purge.command()
@click.confirmation_option(prompt="Are you sure you want to clear Nest data?")
def nest():
    """Purge Nest data"""

    logging.info("Purging Nest data")
    nest_purge_db()
    logging.info("...data has been purged")


@purge.command()
@click.confirmation_option(prompt="Are you sure you want to clear Calendar data?")
def calendar():
    """Purge Calendar data"""

    logging.info("Purging Calendar data")
    gcal_purge_db()
    logging.info("...data has been purged")
