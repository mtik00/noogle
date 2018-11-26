#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
'''
This modules holds common project functions.
'''

# Imports #####################################################################
import logging
import time
from datetime import datetime, timedelta

import click

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '20-JUN-2017'
__license__ = 'Proprietary'


# Globals #####################################################################
def print_log(message, nl=True, log_level=logging.DEBUG):
    ctx = click.get_current_context().obj

    if not ctx.quiet:
        click.echo(message, nl=nl)

    ctx.logger.log(log_level, message)


def format_future_time(minutes=0, seconds=0):
    return (datetime.now() + timedelta(minutes=minutes, seconds=seconds)).strftime('%d-%b-%Y %I:%M %p').upper()
