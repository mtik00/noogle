#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the interface to the application settings.
'''

# Imports #####################################################################
from __future__ import print_function
import os
import re
import pkg_resources

try:
    import ConfigParser
except ImportError:
    import configparser

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '05-JUN-2017'

# Globals #####################################################################

_SETTINGS = None
SETTINGS_FILENAME = 'gcal_nest_settings.ini'
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

    def __init__(self):
        self.conversions = {
            'general.use-logfile': self._to_bool_or_none
        }

        default_settings_file = pkg_resources.resource_filename(
            'gcal_nest', 'conf/gcal_nest_settings.ini')

        self.default_config = ConfigParser.SafeConfigParser()

        with open(default_settings_file) as fp:
            self.default_config.readfp(fp)

        self._user_path = os.path.join(os.path.expanduser('~'), ".gcal_nest", SETTINGS_FILENAME)

        # Keep the two separate (why again?  I can't remember)
        self.user_config = ConfigParser.SafeConfigParser()
        self._loaded_paths = self.user_config.read(FILE_SEARCH)

        self._validate()

    def _to_bool_or_none(self, value):
        '''
        Tries to convert the value to a boolean or None.  We use this
        because `ConfigParser.getboolean()` does not work with None.
        '''
        if value is None:
            return None

        return bool(re.match(r'^[1ty]', str(value), re.IGNORECASE))

    def _validate(self):
        '''
        Validates the settings to ensure they're correct.
        '''
        start = self.get('google calendar.default-start-time')
        if not re.match(r'^\d+:\d{2}$', start):
            raise ValueError(
                ("google calendar.default-start-time ({0}) not "
                 "in correct format: H:mm").format(start)
            )

    def get(self, item):
        '''
        Get a setting in the form of "section.key" (e.g. "nest.device").
        '''
        # func = Settings.conversions.get(key, 'get')
        section, key = item.split('.', 1)

        val = None
        try:
            val = self.user_config.get(section, key)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            val = self.default_config.get(section, key)

        if item in self.conversions:
            return self.conversions[item](val)

        return val

    def set(self, key, value):
        '''
        Set a setting in the form of `"section.key" = value` (e.g. "nest.device", 'Test').
        '''
        section, key = key.split('.', 1)
        try:
            self.user_config.set(section, key, value)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            self.default_config.set(section, key, value)

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
            use_logfile=self.get("general.use-logfile"),
            nest_device=self.get("nest.device"),
            nest_structure=self.get("nest.structure"),
            nest_eco_temperature=self.get("nest.eco-temperature"),
            nest_max_hold=self.get("nest.maximum-hold-days"),
            gcal_calendar_id=self.get("google calendar.calendar-name"),
            default_start_time=self.get("google calendar.default-start-time"),
        )

    def as_string(self, mask=True):
        '''
        Return the settings as a formatted string.
        '''
        lines = []

        for section in self.default_config.sections():
            for key in sorted(self.default_config.options(section)):
                modfied_key = section + '.' + key
                value = self.get(modfied_key)
                if (value is not None) and mask and (modfied_key in SECRET_SETTINGS):
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
