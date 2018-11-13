#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
This module holds the cli `set` commands
'''

# Imports #####################################################################
import click
import arrow

from ..gcal import get_next_events
from ..nest import get_napi_structure, get_nest_api
from ..helpers import print_log

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'
__license__ = 'MIT'


# Globals #####################################################################
@click.group(name='set')
def set_():
    '''Set parameters'''
    ctx = click.get_current_context()

    # No reason to continue if we're in quiet mode
    if ctx.obj.quiet:
        ctx.exit()


@set_.command()
def home():
    '''Sets the thermostate to `home`'''
    ctx = click.get_current_context().obj
    napi = get_nest_api(ctx)
    structure = get_napi_structure(ctx, napi)

    print('Structure: %s' % structure.name)

    if structure.away != 'home':
        structure.away = 'home'
    else:
        print('...already in "home" mode')

    if structure.thermostats[0].mode != 'heat':
        structure.thermostats[0].mode = 'heat'
        print('...changed mode to "heat"')


@set_.command()
def away():
    '''Sets the thermostate to `away`'''
    ctx = click.get_current_context().obj
    napi = get_nest_api(ctx)
    structure = get_napi_structure(ctx, napi)

    print('Structure: %s' % structure.name)

    if structure.away != 'away':
        structure.away = 'away'
    else:
        print('...already in "away" mode')

    if structure.thermostats[0].mode != 'eco':
        structure.thermostats[0].mode = 'eco'
        print('...changed mode to "eco"')

