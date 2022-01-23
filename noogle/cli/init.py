#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
"""
This module holds the cli `init` commands
"""

# Imports #####################################################################
import os
import shutil
from pathlib import Path

import click

from ..db import init as init_db
from ..helpers import print_log
from ..settings import settings
from ..utils import absjoin

# Metadata ####################################################################
TEMPLATE_FOLDER = absjoin
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUN-2017"
__license__ = "Proprietary"


# Globals #####################################################################
@click.group(name="init")
def init():
    """Initialize app"""
    ctx = click.get_current_context()

    # No reason to continue if we're in quiet mode
    if ctx.obj.quiet:
        ctx.exit()


@init.command()
@click.confirmation_option(prompt="Are you sure you want to create a new app?")
def all():
    """Initialize all app settings/data"""

    print_log("Creating all folders/files")

    # Create the instance folders
    base = Path(settings.general.base_config_folder)
    if not base.is_dir():
        base.mkdir(parents=True)
        print_log(f"...{base} has been created")

    for folder_name in ["data", "tokens"]:
        folder = base / folder_name
        if not folder.is_dir():
            folder.mkdir(parents=True)
            print_log(f"...{folder} has been created")

    # initialize the DB
    init_db()
    print_log("...DB has been initialized")


@init.command(name="db")
def init_database():
    """Initialize the database."""
    init_db()
