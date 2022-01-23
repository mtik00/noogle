#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module holds the cli `logging` commands
"""

import glob
import os

import click

from ..settings import settings
from pathlib import Path


@click.group()
def logs():
    """Control the log files"""
    pass


@logs.command()
def clear():
    """Clears the log files"""
    if not settings.logging.logfile:
        return

    path = Path(settings.logging.logfile)
    path.write_text("")
