#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script is used to interface with the noogle package from the command
line.
"""
# pylint:disable=W0212

# Imports #####################################################################
import click

from .. import __version__ as library_version

from ..db import session
from ..settings import get_settings
from .dev import dev
from .init import init
from .logs import logs
from .main import go
from .service import service
from .set_ import set_
from .settings import settings
from .setup import setup
from .shell import shell
from .show import show

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUN-2017"
__version__ = "0.1.0a"


HELP = """
noogle v{0}
""".format(
    library_version
)


class Ctx(object):
    """The context object"""

    def __init__(self):
        self.project_settings = get_settings()
        self.session = None
        self.quiet = False
        self.napi = None
        self.debug = False


CTX = click.make_pass_decorator(Ctx, ensure=True)


@click.group(help=HELP)
@click.option("--quiet", "-q", is_flag=True, help="Only report errors")
@click.option(
    "--debug/--no-debug", "-d", is_flag=True, default=False, help="Debug use only"
)
@CTX
def cli(ctx, quiet, debug):
    """Run the noogle command-line application"""
    ctx.quiet = quiet
    ctx.debug = debug
    ctx.session = session


cli.add_command(show)
cli.add_command(init)
cli.add_command(setup)
cli.add_command(settings)
cli.add_command(go)
cli.add_command(set_)
cli.add_command(service)
cli.add_command(dev)
cli.add_command(logs)
cli.add_command(shell)
