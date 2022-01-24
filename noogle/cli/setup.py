#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
"""
This module holds the cli `setup` commands
"""

# Imports #####################################################################
import sys

import click

from ..gcal import setup as gcal_setup
from ..nest import NestAPI


# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUN-2017"
__license__ = "Proprietary"


# Globals #####################################################################
@click.group()
def setup():
    """Run the setup for Google calendar or Nest"""
    pass


@setup.command()
def gcal():
    """Set up Google calendar"""
    gcal_setup()


@setup.command()
def nest():
    """Set up Nest"""
    ctx = click.get_current_context().obj
    ctx.logger.debug("calling `NestApi.show()`")
    NestAPI().show()
    ctx.logger.debug("...done")
