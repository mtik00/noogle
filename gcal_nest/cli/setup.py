#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
'''
This module holds the cli `setup` commands
'''

# Imports #####################################################################
import sys

import click

from ..gcal import setup as gcal_setup
from ..nest_control import setup as nest_setup


# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'
__license__ = 'Proprietary'


# Globals #####################################################################
@click.group()
def setup():
    '''Run the setup for Google calendar or Nest'''
    pass


@setup.command()
@click.option(
    '--noauth-local-webserver',
    is_flag=True,
    help="don't use a local webserver for authentication")
def gcal(noauth_local_webserver):
    '''Set up Google calendar'''
    # We need to change sys.argv to align with the google setup.
    if noauth_local_webserver:
        sys.argv = sys.argv[0] + '--noauth-local-webserver'
    else:
        sys.argv = [sys.argv[0]]

    gcal_setup(noauth_local_webserver)


@setup.command()
def nest():
    '''Set up Nest'''
    ctx = click.get_current_context().obj
    ctx.logger.debug('calling `nest_setup`')
    nest_setup(ctx)
    ctx.logger.debug('...done')