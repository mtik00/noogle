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

import click

from ..db import init as init_db
from ..helpers import print_log
from ..settings import (
    BASE_CONFIG_FOLDER,
    CONFIG_FOLDER,
    DATA_FOLDER,
    DEPLOY_CONFIG_PATH,
    SETTINGS_FOLDER,
    SETTINGS_PATH,
    TOKEN_FOLDER,
    get_settings,
)
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
    if not os.path.isdir(BASE_CONFIG_FOLDER):
        os.makedirs(BASE_CONFIG_FOLDER)
        print_log(f"...{BASE_CONFIG_FOLDER} has been created")

    for folder in [CONFIG_FOLDER, DATA_FOLDER, SETTINGS_FOLDER, TOKEN_FOLDER]:
        if not os.path.isdir(folder):
            os.makedirs(folder)
            print_log(f"...{folder} has been created")

    # initialize the DB
    init_db()
    print_log("...DB has been initialized")

    # Create the app settings
    if not os.path.isfile(SETTINGS_PATH):
        get_settings().make_user_settings()
        print_log(f"...{SETTINGS_PATH} has been created")

    # Create the deploy settings
    if not os.path.isfile(DEPLOY_CONFIG_PATH):
        src = absjoin(
            os.path.dirname(__file__), "dev", "templates", "deploy-sample.yaml"
        )
        shutil.copyfile(src, DEPLOY_CONFIG_PATH)

    # Create a sample `env.sh`
    env_dest = absjoin(BASE_CONFIG_FOLDER, "env.sh")
    if not os.path.isfile(env_dest):
        env_src = absjoin(os.path.dirname(__file__), "dev", "templates", "env.sh")
        shutil.copyfile(env_src, env_dest)

    print_log("...done")

    print_log(f"Your *instance* folder has been set up at {BASE_CONFIG_FOLDER}")
    print_log(f"..you **MUST** configure {env_dest} and {SETTINGS_PATH}")
    print_log(
        f"...if this machine is used for deployment, you also must configure {DEPLOY_CONFIG_PATH}"
    )
    print_log(f"...you must also put your token files in {TOKEN_FOLDER}")


@init.command(name="db")
def init_database():
    """Initialize the database."""
    init_db()


@init.command()
@click.confirmation_option(prompt="Are you sure you want to clear the settings?")
def settings():
    """
    Sets default settings
    """
    ctx = click.get_current_context().obj

    print_log("Initializing user settings...", nl=False)
    ctx.project_settings.make_user_settings()
    print_log("...done")
    print_log("...settings file at: %s" % ctx.project_settings._user_path)
