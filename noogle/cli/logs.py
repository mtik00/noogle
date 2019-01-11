#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module holds the cli `logging` commands
"""

import glob
import os

import click

from ..settings import DEPLOY_SETTINGS

# Globals #####################################################################


@click.group()
def logs():
    """Control the log files"""
    pass


@logs.command()
def clear():
    """Clears the log files"""
    logdir = DEPLOY_SETTINGS.get("app_log_dir")
    if os.path.isdir(logdir):
        files = glob.glob(f"{logdir}/*")
        for f in files:
            open(f, "w")
    else:
        raise Exception("Could not find log folder")
