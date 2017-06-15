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
import argparse

from gcal_nest.logger import get_logger
from gcal_nest.settings import get_settings
from gcal_nest import __version__ as library_version
from gcal_nest.gcal import setup as gcal_setup, get_next_events
from gcal_nest.nest_control import setup as nest_setup

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'
__version__ = '1.0.0'


def parse_args(default_args=None):
    '''Parse the command-line options'''
    parser = argparse.ArgumentParser(description='CLI for gcal_nest')
    parser.prog = 'gcal_nest'

    parser.add_argument('--events', help='Shows upcoming events', action='store_true')

    ###########################################################################
    settings_group = parser.add_argument_group('settings')
    settings_group.add_argument(
        '--show-settings', help='Shows the project settings',
        action="store_true")
    settings_group.add_argument(
        '--make-user-settings', help='Creates a settings file in ~/gcal_nest',
        action="store_true")

    ###########################################################################
    setup_group = parser.add_argument_group('setup')
    setup_group.add_argument(
        '--gcal-setup', help='Set up your Google API OAuth credentials',
        action="store_true")
    setup_group.add_argument(
        '--noauth_local_webserver',
        help="Use 'offline' mode when setting up Google API",
        action="store_true")

    setup_group.add_argument(
        '--nest-setup', help='Set up your Nest API OAuth credentials',
        action="store_true")

    return parser.parse_args(default_args)


def show_events():
    events = get_next_events()
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


# Globals #####################################################################
def main():
    '''The main entry point for the CLI application'''
    print("Using gcal_nest v{0}\n".format(library_version))

    get_logger()
    args = parse_args()
    print(args)
    project_settings = get_settings()

    if args.show_settings:
        project_settings.print_settings()
    elif args.make_user_settings:
        project_settings.make_user_settings(display_result=True)
    elif args.gcal_setup:
        # We need to remove our command-line argument from sys.argv so the
        # google script will work.
        sys.argv.remove('--gcal-setup')
        gcal_setup(args.noauth_local_webserver)
    elif args.nest_setup:
        nest_setup()
    elif args.events:
        show_events()


if __name__ == '__main__':
    main()
