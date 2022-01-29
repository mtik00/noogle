#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module holds the interface to Google calendar.
"""
# Imports #####################################################################
import arrow
from apiclient import discovery
from googleapiclient.errors import HttpError

from .google_auth import get_credentials
from .helpers import print_log
from .models import Event
from .settings import settings

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "08-JUN-2017"


def setup():
    """
    Set up your credentials for access to google calendar.
    """
    events = get_next_gcal_events()
    if not events:
        print_log("No upcoming events found.")
        return

    for event in events:
        e = Event.create_from_gcal(event, commit=False)
        print_log(
            "{:<19s}({:^9}) {}".format(
                e.scheduled_date.format("YYYY-MM-DD h:mmA"), e.state, e.name
            )
        )


def get_next_gcal_events(max_results=10, q_filter="nest", since=None):
    """
    Returns a list of events filtered by ``q_filter``.

    :param int max_results: The maximum number of results to return
    :param str q: This is the "advanced search syntax" item
    :param datetime since: Get the events since this date
    """
    calendar_id = settings.calendar.name

    credentials = get_credentials(
        name="calendar", oauth_token=settings.calendar.token_file
    )
    service = discovery.build("calendar", "v3", credentials=credentials)

    if since:
        since = since.to("UTC").isoformat()
    else:
        lookback = settings.calendar.lookback
        since = (
            arrow.now()
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .shift(days=-1 * lookback)
            .isoformat()
        )

    try:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=since,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
                q=q_filter,
            )
            .execute()
        )
    except HttpError as e:
        if e.resp["status"] == "404":
            raise ValueError(
                'Could not find your calendar: "%s".  Please check your settings!'
                % calendar_id
            )

        raise

    return events_result.get("items", [])
