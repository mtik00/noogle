#!/usr/bin/env python3
"""
Basic application logger with optional logfile.

Usage:
    - modify/remove arrow as neccessary
    - modify `shorten_path` if needed
    - call `init_logger()` as soon as possible
    - use `logging.[debug,info,error,etc]` in your modules.
"""
import logging
import os
from pathlib import Path
from typing import List, Optional

import arrow


def shorten_path(path):
    """
    This seems like a pretty bad idea, but I'm doing it anyway.
    I want to convert an asbolute path to a kind of module-relative path.

    Something like:
        /usr/src/app/free_game_notifier/notifier/slack.py
    would be shortend to:
        notifier/slack.py
    """
    base, _ = os.path.split(__file__)
    return path.replace(base + os.path.sep, "")


class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""

    def __init__(self, timezone, *args, **kwargs):
        self._timezone = timezone
        super().__init__(*args, **kwargs)

    def format(self, record):
        """shorten the absolute path"""
        record.pathname = shorten_path(record.pathname)
        return super().format(record)

    def converter(self, timestamp):
        dt = arrow.get(timestamp)
        return dt.to(self._timezone)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return s


def set_root_level(level):
    logging.getLogger().setLevel(level)


def init_logger(
    timezone: str,
    logfile: Optional[Path] = None,
    logfile_mode: str = "a",
    logfile_level: int = logging.DEBUG,
    debug: bool = False,
    third_party_loggers: List[str] = [],
) -> None:

    for module in third_party_loggers:
        logging.getLogger(module).setLevel(logging.ERROR)

    fmt = Formatter(
        timezone=timezone,
        fmt="%(asctime)s {%(pathname)20s:%(lineno)3s} %(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S %Z",
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    stream_handler.setLevel(logging.INFO)
    if debug:
        stream_handler.setLevel(logging.DEBUG)

    handlers: List[logging.Handler] = [stream_handler]

    if logfile:
        file_handler = logging.FileHandler(logfile, logfile_mode)
        file_handler.setLevel(logfile_level)
        file_handler.setFormatter(fmt)
        handlers.append(file_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
