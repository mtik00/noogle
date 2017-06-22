#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
'''
This module holds the cli `init` commands
'''

# Imports #####################################################################
import click

from ..helpers import print_log

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'
__license__ = 'Proprietary'


# Globals #####################################################################
@click.command(name="init")
@click.confirmation_option(prompt='Are you sure you want to clear the cache and settings?')
def init():
    '''
    Clears the cache and sets default settings
    '''
    ctx = click.get_current_context().obj

    print_log('Initializing cache...', nl=False)
    ctx.cache.init()
    print_log('...done')
    print_log('...cache file at: %s' % ctx.cache.default_path)

    print_log('Initializing user settings...', nl=False)
    ctx.project_settings.make_user_settings()
    print_log('...done')
    print_log('...settings file at: %s' % ctx.project_settings._user_path)