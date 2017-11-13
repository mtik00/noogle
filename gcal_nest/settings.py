#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the interface to the application settings.
'''

# Imports #####################################################################
from __future__ import print_function
import os
import re
import ConfigParser
import pkg_resources

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '05-JUN-2017'

# Globals #####################################################################

_SETTINGS = None
SETTINGS_FILENAME = 'gcal_nest.ini'
USER_FOLDER = os.path.join(os.path.expanduser('~'), ".gcal_nest")
FILE_SEARCH = [
    os.path.join("/etc/gcal_nest", SETTINGS_FILENAME),
    os.path.join(USER_FOLDER, SETTINGS_FILENAME),
    os.path.abspath(os.path.join(os.curdir, SETTINGS_FILENAME)),
]

# These settings will be removed from `as_string`
SECRET_SETTINGS = ['nest.product-id', 'nest.product-secret']


def get_settings():
    '''
    Return, or create and return, the settings object.
    '''
    global _SETTINGS
    if _SETTINGS:
        return _SETTINGS

    _SETTINGS = Settings()
    return _SETTINGS


def absjoin(*args):
    '''Returns the absolute path returned from `abs.join(*args)`.'''
    return os.path.abspath(os.path.join(*args))


class Settings(object):
    '''A simple interface to a project's settings stored as a dictionary.'''
    settings = {
        'general': {
            'use-logfile': True
        },
        'nest': {
            'structure': None,
            'device': None,
            'eco-temperature': 50,
            'maximum-hold-days': 10,
            'product-id': None,
            'product-secret': None
        },
        'calendar': {
            'name': 'primary',
            'default-start-time': '9:00',
            'lookback': 2,
        }
    }

    def __init__(self):
        # Do our own converstions for certain items.  The ones built in to
        # ConfigParser (e.g. `.getboolean()`) are finicky.
        self.conversions = {
            'general.use-logfile': self._to_bool_or_none,
            'calendar.lookback': self._to_int
        }

        config = ConfigParser.SafeConfigParser()

        self._user_path = os.path.join(
            os.path.expanduser('~'),
            '.gcal_nest',
            SETTINGS_FILENAME)

        self._loaded_paths = config.read(FILE_SEARCH)

        for section in config.sections():
            for key, value in config.items(section):
                if value is not None:
                    self.settings[section][key] = value

        self._validate()

    def _to_int(self, value, base=10):
        '''
        Tries to convert the value to an integer or None.
        '''
        if isinstance(value, int):
            return value
        elif (value is None) or (not value.isdigit()):
            return None

        return int(value, base=base)

    def _to_bool_or_none(self, value):
        '''
        Tries to convert the value to a boolean or None.  We use this
        because `ConfigParser.getboolean()` does not work with None.
        '''
        if isinstance(value, bool):
            return value
        elif value is None:
            return None

        return bool(re.match(r'^[1ty]', str(value), re.IGNORECASE))

    def _validate(self):
        '''
        Validates the settings to ensure they're correct.
        '''
        start = self.settings['calendar']['default-start-time']
        if not re.match(r'^\d+:\d{2}$', start):
            raise ValueError(
                ("calendar.default-start-time ({0}) not "
                 "in correct format: H:mm").format(start)
            )

    def get(self, item):
        '''
        Get a setting in the form of "section.key" (e.g. "nest.device").
        '''
        section, key = item.split('.', 1)
        val = self.settings.get(section, {}).get(key, None)

        if item in self.conversions:
            return self.conversions[item](val)

        return val

    def set(self, item, value):
        '''
        Set a setting in the form of `"section.key" = value` (e.g. "nest.device", 'Test').
        '''
        section, key = item.split('.', 1)
        self.settings[section][key] = value

    def as_ini_file(self):
        '''
        Return the settings formatted as in INI file.  This would be used to
        create a user-config file.
        '''
        default_settings_file = pkg_resources.resource_filename(
            'gcal_nest', 'conf/conf-format.ini')

        text = open(default_settings_file).read()

        # FYI, we don't need to convert these values; They will default to
        # string(), which is fine.
        return text.format(
            use_logfile="" if self.settings['general']['use-logfile'] is None else self.settings['general']['use-logfile'],
            nest_device="" if self.settings['nest']['device'] is None else self.settings['nest']['device'],
            nest_structure="" if self.settings['nest']['structure'] is None else self.settings['nest']['structure'],
            nest_eco_temperature="" if self.settings['nest']['eco-temperature'] is None else self.settings['nest']['eco-temperature'],
            nest_max_hold="" if self.settings['nest']['maximum-hold-days'] is None else self.settings['nest']['maximum-hold-days'],
            gcal_calendar_id="" if self.settings['calendar']['name'] is None else self.settings['calendar']['name'],
            default_start_time="" if self.settings['calendar']['default-start-time'] is None else self.settings['calendar']['default-start-time'],
            lookback="" if self.settings['calendar']['lookback'] is None else self.settings['calendar']['lookback'],
        )

    def as_string(self, mask=True):
        '''
        Return the settings as a formatted string.
        '''
        lines = []

        for section in sorted(self.settings.keys()):
            for key in sorted(self.settings[section].keys()):
                value = self.settings[section][key]
                modified = section + '.' + key
                if (value is not None) and mask and (modified in SECRET_SETTINGS):
                    lines.append("%s.%s = <MASKED>" % (section, key))
                elif value is not None:
                    lines.append("%s.%s = %s" % (section, key, value))
                else:
                    lines.append("%s.%s = <EMPTY>" % (section, key))

        return "\n".join(lines)

    def save(self):
        '''
        Stores the settings to the user's configuration file.
        '''
        path = self._user_path
        dirname = os.path.dirname(path)

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        text = self.as_ini_file()
        open(path, 'wb').write(text)

    def print_settings(self):
        '''Display the project settings'''
        print(self.as_string())

        if self._loaded_paths:
            print("\nSettings files loaded in the following order:")
            for index, path in enumerate(self._loaded_paths):
                print("    %i) %s" % (index + 1, path))

        print("")

    def make_user_settings(self, display_result=False):
        '''
        Create a user settings file.
        '''
        self.save()

        if display_result:
            print("Settings file stored at: %s" % self._user_path)
