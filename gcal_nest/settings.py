#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the interface to the application settings.
'''

# Imports #####################################################################
import os
import json
import pkg_resources

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '05-JUN-2017'

# Globals #####################################################################
_SETTINGS = None
SETTINGS_FILENAME = 'gcal_nest_settings.json'
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
DIR_SEARCH = [
    os.curdir,
    os.path.join(os.path.expanduser('~'), "gcal_nest"),
    "/etc/gcal_nest"
]


def get_settings():
    '''
    Return, or create and return, the settings object.
    '''
    global _SETTINGS
    if _SETTINGS:
        return _SETTINGS

    _SETTINGS = JSONSettings()
    return _SETTINGS


def absjoin(*args):
    '''Return the absolute path of the joined paths'''
    return os.path.abspath(os.path.join(*args))


class Settings(object):
    '''A simple interface to a project's settings stored as a dictionary.'''
    def __init__(self):
        self._default_settings = {}
        self._user_settings = {}
        self._settings = {}

    @property
    def settings(self):
        return dict(self._settings)

    def __getitem__(self, key):
        '''Allow ``[]`` access to the settings.'''
        return self._settings[key]

    def __setitem__(self, key, value):
        '''Allow ``[]=X`` to change a setting.'''
        self._settings[key] = value


class JSONSettings(Settings):
    '''
    This class provides an interface for settings stored in a JSON file.
    '''
    def __init__(self, path=None, search_dirs=None):
        super(JSONSettings, self).__init__()

        default_settings_file = pkg_resources.resource_filename(
            'gcal_nest', 'conf/gcal_nest_settings.json')

        self._default_settings = json.loads(open(default_settings_file).read())

        self._path = path or self._find_settings_file(search_dirs)

        if self._path and os.path.exists(self._path):
            # Merge these w/ the default
            self._user_settings = json.loads(open(self._path).read())

        self._settings = dict(self._default_settings)
        self._settings.update(self._user_settings)

    def _find_settings_file(self, search_dirs):
        '''
        Search through each directory for the settings file.
        '''
        search_dirs = search_dirs or DIR_SEARCH

        for search_dir in search_dirs:
            test_path = absjoin(search_dir, SETTINGS_FILENAME)
            if os.path.isfile(test_path):
                return test_path

        return None

    def save(self):
        '''
        Stores the settings file.

        NOTE: This is only used if the user passed in a file path.
        '''
        if self._path:
            text = json.dumps(self._settings, indent=4)
            open(self._path, 'wb').write(text)
