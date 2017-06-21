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
from gcal_nest.nest_control import setup as nest_setup, get_napi_thermostat
from gcal_nest.cache import get_cache
from gcal_nest import main
from gcal_nest.helpers import print_log

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
        self.cache = get_cache()
        self.quiet = False
        self.napi = None


CONTEXT = click.make_pass_decorator(Ctx, ensure=True)


@click.group(help=HELP)
@click.option('--quiet', '-q', is_flag=True, help='Only report errors')
@CONTEXT
def cli(ctx, quiet):
    '''Run the gcal_nest command-line application'''
    ctx.quiet = quiet


@cli.command(name="init")
@click.confirmation_option(prompt='Are you sure you want to clear the cache and settings?')
@CONTEXT
def init(ctx):
    '''
    Clears the cache and sets default settings
    '''
    print_log(ctx, 'Initializing cache...', nl=False)
    ctx.cache.init()
    print_log(ctx, '...done')
    print_log(ctx, '...cache file at: %s' % ctx.cache.default_path)

    print_log(ctx, 'Initializing user settings...', nl=False)
    ctx.project_settings.make_user_settings()
    print_log(ctx, '...done')
    print_log(ctx, '...settings file at: %s' % ctx.project_settings._user_path)


@cli.group()
def show():
    '''Show information'''
    pass


@show.command()
@CONTEXT
@click.option(
    '--max-events', default=10, help='maximum number of events to show')
def events(ctx, max_events):
    '''Display the next events from Google calendar'''

    nest_events = get_next_events(max_results=max_events)

    for event in nest_events:
        print(
            "{:<19s}({:^9}) {}".format(
                event.scheduled_date.format('YYYY-MM-DD h:mmA'),
                event.state,
                event.name)
        )


@show.command()
@CONTEXT
def cache(ctx):
    '''
    Shows the cached events
    '''
    # For the pager to work, we need to create one big string.
    str_events = []
    for event in ctx.cache.events():
        str_events.append(
            "{:<19s}({:^9}) {}".format(
                event.scheduled_date.format('YYYY-MM-DD h:mmA'),
                event.state,
                event.name)
        )

    click.echo_via_pager("\n".join(str_events))


@show.command()
@CONTEXT
def thermostat(ctx):
    '''Show the current thermostat info'''
    thermostat = get_napi_thermostat(ctx)

    print_log(
        ctx,
        '%s : %s' % (
            thermostat.structure.name,
            thermostat.name)
    )

    setpoint = "%s%s (%s)" % (thermostat.target, thermostat.temperature_scale, thermostat.mode)
    if thermostat.mode.lower() == 'eco':
        setpoint = "%s%s (eco)" % (thermostat.eco_temperature.low, thermostat.temperature_scale)
    print_log(ctx, '...current setpoint: %s' % setpoint)

    print_log(
        ctx,
        '...current temperature: %s%s' % (
            thermostat.temperature,
            thermostat.temperature_scale
        )
    )

    print_log(
        ctx,
        '...current humidity: %s%%' % thermostat.humidity
    )

    print_log(
        ctx,
        '...state: %s' % thermostat.hvac_state
    )

    print_log(
        ctx,
        '...eco temperatures: low={low}{scale}, high={high}{scale}'.format(
            low=thermostat.eco_temperature.low,
            scale=thermostat.temperature_scale,
            high=thermostat.eco_temperature.high
        )
    )


@cli.group()
def setup():
    '''Run the setup for Google calendar or Nest'''
    pass


@setup.command()
@click.option(
    '--noauth-local-webserver',
    is_flag=True,
    help="don't use a local webserver for authentication")
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
    ctx.logger.debug('calling `nest_setup`')
    nest_setup(ctx)
    ctx.logger.debug('...done')


@cli.command()
@CONTEXT
def go(ctx):
    '''Run the main function'''
    ctx.logger.debug('calling `main`')
    return main(ctx)
    ctx.logger.debug('...done')


@cli.group()
def settings():
    '''Application settings'''
    pass


@settings.command(name="make")
@CONTEXT
def make_settings(ctx):
    '''Creates a copy of application settings in your home directory'''
    ctx.logger.debug('calling `make_user_settings`')
    ctx.project_settings.make_user_settings()
    ctx.logger.debug('...done')


@settings.command(name="show")
def show_settings2():
    '''Display the settings.'''

    get_settings().print_settings()


if __name__ == '__main__':
    cli()
