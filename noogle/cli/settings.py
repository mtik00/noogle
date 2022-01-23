#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
"""
This module holds the cli `settings` commands
"""

from pprint import pprint

# Imports #####################################################################
import click

from ..settings import settings as app_settings

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUN-2017"
__license__ = "Proprietary"


# Globals #####################################################################
@click.group()
def settings():
    """Application settings"""
    pass


@settings.command()
def show():
    """Display the settings."""
    pprint(app_settings.dict())
