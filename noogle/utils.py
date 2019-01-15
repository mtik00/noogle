import os

import arrow


def absjoin(*args):
    return os.path.abspath(os.path.join(*args))


def get_scheduled_date(gcal_event):
    """
    Returns an `Arrow` object representing the scheduled date/time of the event.
    """
    if not (("start" in gcal_event) and ("dateTime" in gcal_event["start"])):
        raise ValueError("Can't find `['start']['dateTime']` in event")

    return arrow.get(gcal_event["start"].get("dateTime"))
