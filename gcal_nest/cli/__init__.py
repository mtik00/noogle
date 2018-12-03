#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script is used to interface with the gcal_nest package from the command
line.
"""
# pylint:disable=W0212

# Imports #####################################################################
from __future__ import print_function

import click

from .. import __version__ as library_version
from ..logger import get_logger
from ..settings import get_settings
from ..cache import get_cache

from .show import show
from .init import init
from .setup import setup
from .settings import settings
from .main import go
from .set_ import set_
from .service import service

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUN-2017"
__version__ = "1.0.0"


HELP = """
gcal_nest v{0}
""".format(
    library_version
)


class Ctx(object):
    """The context object"""

    def __init__(self):
        self.logger = get_logger()
        self.project_settings = get_settings()
        self.cache = None
        self.quiet = False
        self.napi = None
        self.debug = False


CTX = click.make_pass_decorator(Ctx, ensure=True)


@click.group(help=HELP)
@click.option("--quiet", "-q", is_flag=True, help="Only report errors")
@click.option(
    "--debug/--no-debug", "-d", is_flag=True, default=True, help="Debug use only"
)
@CTX
def cli(ctx, quiet, debug):
    """Run the gcal_nest command-line application"""
    ctx.quiet = quiet
    ctx.debug = debug
    ctx.cache = get_cache(debug)


cli.add_command(show)
cli.add_command(init)
cli.add_command(setup)
cli.add_command(settings)
cli.add_command(go)
cli.add_command(set_)
cli.add_command(service)
