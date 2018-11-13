#!/usr/bin/env python2
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#  Copyright (C) 2017 Broadcom Ltd.  All rights reserved.                     #
#                                                                             #
###############################################################################
'''
This module holds the cli `settings` commands
'''

# Imports #####################################################################
import click


# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'
__license__ = 'Proprietary'


# Globals #####################################################################
@click.group()
def settings():
    '''Application settings'''
    pass


@settings.command()
def make():
    '''Creates a copy of application settings in your home directory'''

    ctx = click.get_current_context().obj

    ctx.logger.debug('calling `make_user_settings`')
    ctx.project_settings.make_user_settings(display_result=True)
    ctx.logger.debug('...done')


@settings.command()
def show():
    '''Display the settings.'''
    ctx = click.get_current_context().obj
    ctx.project_settings.print_settings()


@settings.command()
@click.argument('name')
@click.argument('value')
def set(name, value):
    '''Set a setting'''
    project_settings = click.get_current_context().obj.project_settings
    project_settings.set(name, value)
    project_settings.save()
    project_settings.print_settings()


@settings.command()
@click.argument('name')
def get(name):
    '''Show a setting'''
    project_settings = click.get_current_context().obj.project_settings
    value = project_settings.get(name)
    click.echo('%s: %s' % (name, value))
