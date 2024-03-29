import os

import arrow


def absjoin(*args):
    if any(args):
        return os.path.abspath(os.path.join(*args))

    return None


def get_scheduled_date(gcal_event):
    """
    Returns an `Arrow` object representing the scheduled date/time of the event.
    """
    if not (("start" in gcal_event) and ("dateTime" in gcal_event["start"])):
        raise ValueError("Can't find `['start']['dateTime']` in event")

    return arrow.get(gcal_event["start"].get("dateTime"))


def is_winter(date: arrow.Arrow = arrow.now()) -> bool:
    """
    Returns `True` if the date is considered winter.
    """
    month = date.date().month
    return (1 <= month <= 4) or (10 <= month <= 12)


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * (9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * (5 / 9)
