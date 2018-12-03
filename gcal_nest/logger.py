#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module holds the single logging object for the project.
"""

# Imports #####################################################################
import os
import logging

# from .settings import settings

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "08-JUN-2017"


# Globals #####################################################################
LOGGER = None


def get_logger(
    name=None,
    screen_level=logging.INFO,
    logfile_path=None,
    logfile_level=logging.DEBUG,
    logfile_mode="wb",
):
    """Returns a logging object.

    You should use the parameterized function once to initialize
    the logger.  Subsequent calls should use ``get_logger()`` to
    use the common logging object.

    :param str name: The name of the logger; defaults to the script name
    :param int screen_level: The level of the screen logger
    :param str logfile_path: The path of the log file, if any
    :param int logfile_level: The level of the file logger
    :param str logfile_mode: The file mode of the file logger

    :rtype: logging.logger
    :returns: A common logger for a project
    """
    global LOGGER
    if LOGGER:
        return LOGGER

    name = name or os.path.splitext(os.path.basename(__file__))[0]

    _format = "%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s"

    _logger = logging.getLogger(name)
    _logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    screen_formatter = logging.Formatter(_format)
    console_handler.setFormatter(screen_formatter)
    console_handler.setLevel(screen_level)
    _logger.addHandler(console_handler)

    if logfile_path:
        logfile_formatter = logging.Formatter(_format)
        file_handler = logging.FileHandler(logfile_path, logfile_mode)
        file_handler.setLevel(logfile_level)
        file_handler.setFormatter(logfile_formatter)
        _logger.addHandler(file_handler)

    LOGGER = _logger
    return _logger
