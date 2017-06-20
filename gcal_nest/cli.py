#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This script is used to interface with the gcal_nest package from the command
line.
'''
# pylint:disable=W0212

# Imports #####################################################################
from __future__ import print_function
import sys

import click

from gcal_nest.logger import get_logger
from gcal_nest.settings import get_settings
from gcal_nest import __version__ as library_version
from gcal_nest.gcal import setup as gcal_setup, get_next_events
from gcal_nest.nest_control import setup as nest_setup
from gcal_nest.cache import get_cache

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'
__version__ = '1.0.0'


HELP = '''
gcal_nest v{0}
'''.format(library_version)


class Ctx(object):
    '''The context object'''
    def __init__(self):
        self.logger = get_logger()
        self.project_settings = get_settings()


CONTEXT = click.make_pass_decorator(Ctx, ensure=True)


@click.group(help=HELP)
def cli():
    '''Run the gcal_nest command-line application'''
    pass


@cli.group()
def show():
    '''Show information'''
    pass


@show.command()
@CONTEXT
def events(ctx):
    '''Display the next events.'''

    nest_events, _ = get_next_events()

    for event in nest_events:
        print(
            "{:<19s}({:^9}) {}".format(
                event.scheduled_date.format('YYYY-MM-DD h:mmA'),
                event.state,
                event.name)
        )


@cli.group()
def setup():
    '''Run the setup for Google calendar or Nest'''
    pass


@setup.command()
@click.option('--noauth-local-webserver', is_flag=True)
@CONTEXT
def gcal(ctx, noauth_local_webserver):
    '''Set up Google calendar'''
    ctx

    # We need to change sys.argv to align with the google setup.
    if noauth_local_webserver:
        sys.argv = sys.argv[0] + '--noauth-local-webserver'
    else:
        sys.argv = [sys.argv[0]]

    gcal_setup(noauth_local_webserver)


@setup.command()
@CONTEXT
def nest(ctx):
    '''Set up Nest'''
    ctx
    nest_setup()


@cli.command()
@CONTEXT
def go(ctx):
    '''Run the main function'''
    # Grab the next 10 events
    my_events, _ = get_next_events(max_results=10)

    # Add them to the cache if they aren't already there
    cache = get_cache()

    for event in my_events:
        if not cache.exists(event.event_id):
            print("caching new event: {0}".format(event))
            cache.add_event(event)

    # Get all events that haven't been actioned
    my_events = [x for x in cache.waiting()]
    print(my_events)


@cli.group()
def settings():
    '''Application settings'''
    pass


@settings.command(name="make")
@CONTEXT
def make_settings(ctx):
    '''Creates a copy of application settings in your home directory'''
    ctx.project_settings.make_user_settings()


@settings.command(name="show")
def show_settings2():
    '''Display the settings.'''

    get_settings().print_settings()


if __name__ == '__main__':
    cli()
