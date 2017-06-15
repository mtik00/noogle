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
from pprint import pprint as pp

from gcal_nest.logger import get_logger
from gcal_nest.settings import get_settings
from gcal_nest import __version__ as library_version

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'
__version__ = '1.0.0'


def parse_args(default_args=None):
    '''Parse the command-line options'''
    parser = argparse.ArgumentParser(description='CLI for gcal_nest')
    parser.prog = 'gcal_nest'

    parser.add_argument(
        '--show-settings', help='Shows the project settings',
        action="store_true")

    args = parser.parse_args(default_args)

    if not(default_args or len(sys.argv[1:])):
        parser.print_help()
        sys.exit(1)

    return args


def show_settings(project_settings):
    '''Display the project settings'''
    print("=== Default settings:\n")
    pp(project_settings._default_settings, indent=4)
    print("")

    print("=== User settings:\n")
    if project_settings._user_settings:
        print("    %s\n" % project_settings._path)
        pp(project_settings._user_settings, indent=4)
        print("\n")
        print("=== Calculated settings:\n")
        pp(project_settings._settings, indent=4)
    else:
        print("    <NONE>")

    print("")


# Globals #####################################################################
def main():
    '''The main entry point for the CLI application'''
    print("Using gcal_nest v{0}\n".format(library_version))

    get_logger()

    args = parse_args()

    project_settings = get_settings()

    if args.show_settings:
        show_settings(project_settings)


if __name__ == '__main__':
    main()
