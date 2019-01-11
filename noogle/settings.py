#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module holds the interface to the application settings.
"""

# Imports #####################################################################
from __future__ import print_function

import os
import re

import pkg_resources

import ruamel.yaml

from .utils import absjoin

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser


# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "05-JUN-2017"

# Globals #####################################################################

_SETTINGS = None
SETTINGS_FILENAME = "noogle.ini"
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_FOLDER = absjoin(THIS_DIR, "..", "instance")

TOKEN_FOLDER = absjoin(INSTANCE_FOLDER, "tokens")
DATA_FOLDER = absjoin(INSTANCE_FOLDER, "data")
CONFIG_FOLDER = absjoin(INSTANCE_FOLDER, "config")

SITE_YAML = absjoin(CONFIG_FOLDER, "site.yaml")

SETTINGS_FOLDER = os.getenv("SETTINGS_FOLDER", INSTANCE_FOLDER)
SETTINGS_PATH = absjoin(SETTINGS_FOLDER, SETTINGS_FILENAME)
FILE_SEARCH = [SETTINGS_PATH]

# These settings will be removed from `as_string`
SECRET_SETTINGS = ["nest.product-id", "nest.product-secret", "nest.access-token"]

SITE = {}
if os.path.exists(SITE_YAML):
    with open(SITE_YAML) as fh:
        SITE = ruamel.yaml.safe_load(fh)


def get_settings():
    """
    Return, or create and return, the settings object.
    """
    global _SETTINGS
    if _SETTINGS:
        return _SETTINGS

    _SETTINGS = Settings()
    return _SETTINGS


class Settings(object):
    """A simple interface to a project's settings stored as a dictionary."""

    settings = {
        "general": {"use-logfile": True},
        "nest": {
            "structure": None,
            "thermostat": None,
            "eco-temperature": 50,
            "maximum-hold-days": 10,
            "product-id": None,
            "product-secret": None,
            "access-token": None,
        },
        "calendar": {
            "name": "primary",
            "default-home-time": "9:00",
            "default-away-time": "19:00",
            "lookback": 2,
            "timezone": "MST",
        },
    }

    def __init__(self):
        # Do our own converstions for certain items.  The ones built in to
        # ConfigParser (e.g. `.getboolean()`) are finicky.
        self.conversions = {
            "general.use-logfile": self._to_bool_or_none,
            "calendar.lookback": self._to_int,
        }

        config = ConfigParser()

        self._user_path = SETTINGS_PATH
        self._loaded_paths = config.read(FILE_SEARCH)

        for section in config.sections():
            for key, value in config.items(section):
                if value is not None:
                    self.settings[section][key] = value

        self._validate()

    def _to_int(self, value, base=10):
        """
        Tries to convert the value to an integer or None.
        """
        if isinstance(value, int):
            return value
        elif (value is None) or (not value.isdigit()):
            return None

        return int(value, base=base)

    def _to_bool_or_none(self, value):
        """
        Tries to convert the value to a boolean or None.  We use this
        because `ConfigParser.getboolean()` does not work with None.
        """
        if isinstance(value, bool):
            return value
        elif value is None:
            return None

        return bool(re.match(r"^[1ty]", str(value), re.IGNORECASE))

    def _validate(self):
        """
        Validates the settings to ensure they're correct.
        """
        start = self.settings["calendar"]["default-home-time"]
        if not re.match(r"^\d+:\d{2}$", start):
            raise ValueError(
                (
                    "calendar.default-home-time ({0}) not " "in correct format: H:mm"
                ).format(start)
            )

    def get(self, item, default=None):
        """
        Get a setting in the form of "section.key" (e.g. "nest.thermostat").
        """
        section, key = item.split(".", 1)
        val = self.settings.get(section, {}).get(key, default)

        if item in self.conversions:
            return self.conversions[item](val)

        return val

    def set(self, item, value):
        """
        Set a setting in the form of `"section.key" = value` (e.g. "nest.thermostat", 'Test').
        """
        section, key = item.split(".", 1)
        self.settings[section][key] = value

    def as_ini_file(self):
        """
        Return the settings formatted as in INI file.  This would be used to
        create a user-config file.
        """
        default_settings_file = pkg_resources.resource_filename(
            "noogle", "conf/conf-format.ini"
        )

        text = open(default_settings_file).read()

        # FYI, we don't need to convert these values; They will default to
        # string(), which is fine.
        return text.format(
            use_logfile=""
            if self.settings["general"]["use-logfile"] is None
            else self.settings["general"]["use-logfile"],
            nest_thermostat=""
            if self.settings["nest"]["thermostat"] is None
            else self.settings["nest"]["thermostat"],
            nest_structure=""
            if self.settings["nest"]["structure"] is None
            else self.settings["nest"]["structure"],
            nest_eco_temperature=""
            if self.settings["nest"]["eco-temperature"] is None
            else self.settings["nest"]["eco-temperature"],
            nest_max_hold=""
            if self.settings["nest"]["maximum-hold-days"] is None
            else self.settings["nest"]["maximum-hold-days"],
            gcal_calendar_id=""
            if self.settings["calendar"]["name"] is None
            else self.settings["calendar"]["name"],
            default_start_time=""
            if self.settings["calendar"]["default-home-time"] is None
            else self.settings["calendar"]["default-home-time"],
            lookback=""
            if self.settings["calendar"]["lookback"] is None
            else self.settings["calendar"]["lookback"],
            timezone=""
            if self.settings["calendar"]["timezone"] is None
            else self.settings["calendar"]["timezone"],
        )

    def as_string(self, mask=True):
        """
        Return the settings as a formatted string.
        """
        lines = []

        for section in sorted(self.settings.keys()):
            for key in sorted(self.settings[section].keys()):
                value = self.settings[section][key]
                modified = section + "." + key
                if (value is not None) and mask and (modified in SECRET_SETTINGS):
                    lines.append("%s.%s = <MASKED>" % (section, key))
                elif value is not None:
                    lines.append("%s.%s = %s" % (section, key, value))
                else:
                    lines.append("%s.%s = <EMPTY>" % (section, key))

        return "\n".join(lines)

    def save(self):
        """
        Stores the settings to the user's configuration file.
        """
        path = self._user_path
        dirname = os.path.dirname(path)

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        text = self.as_ini_file()

        open(path, "wb").write(text.encode("utf-8"))

    def print_settings(self):
        """Display the project settings"""
        print(self.as_string())

        if self._loaded_paths:
            print("\nSettings files loaded in the following order:")
            for index, path in enumerate(self._loaded_paths):
                print("    %i) %s" % (index + 1, path))

        print("")

    def make_user_settings(self, display_result=False):
        """
        Create a user settings file.
        """
        self.save()

        if display_result:
            print("Settings file stored at: %s" % self._user_path)
