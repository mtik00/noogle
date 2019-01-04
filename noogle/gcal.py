#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module holds the interface to Google calendar.
"""

# Imports #####################################################################
from __future__ import print_function
import os
import sys
import argparse
import httplib2

import arrow
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.errors import HttpError

from .settings import SETTINGS_FOLDER, get_settings

# from .event import Event

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "08-JUN-2017"


# Globals #####################################################################
SCOPES = "https://www.googleapis.com/auth/calendar.readonly"
CLIENT_SECRET_FILE = os.path.join(SETTINGS_FOLDER, "google-client-secret.json")
APPLICATION_NAME = "Google Calendar API Python Quickstart"


def get_credentials(noauth_local_webserver=False):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    NOTE: This was modified from
    https://developers.google.com/google-apps/calendar/quickstart/python

    Returns:
        Credentials, the obtained credential.
    """
    if not os.path.exists(CLIENT_SECRET_FILE):
        print("ERROR: Google client secrect not found at: %s" % CLIENT_SECRET_FILE)
        print("...Download the JSON credentials from:")
        print("...https://console.developers.google.com/apis/credentials")
        print("...and put them here: %s" % CLIENT_SECRET_FILE)
        print("Dont forget to rename the file!")
        sys.exit(1)

    if not os.path.exists(SETTINGS_FOLDER):
        os.makedirs(SETTINGS_FOLDER)
    credential_path = os.path.join(SETTINGS_FOLDER, "google-calendar.json")

    if noauth_local_webserver:
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args(
            ["--noauth_local_webserver"]
        )
    else:
        flags = None

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print("Storing credentials to " + credential_path)
    return credentials


def setup(auth_local_webserver=False):
    """
    Set up your credentials for access to google calendar.
    """
    noauth_local_webserver = not auth_local_webserver
    get_credentials(noauth_local_webserver=noauth_local_webserver)
    events = get_next_events()
    if not events:
        print("No upcoming events found.")
        return

    for event in events:
        print(
            "{:<19s}({:^9}) {}".format(
                event.scheduled_date.format("YYYY-MM-DD h:mmA"), event.state, event.name
            )
        )


def get_next_events(max_results=10, q_filter="nest", since=None):
    """
    Returns a list of events filtered by ``q_filter``.

    :param int max_results: The maximum number of results to return
    :param str q: This is the "advanced search syntax" item
    :param datetime since: Get the events since this date
    """
    calendar_id = get_settings().get("calendar.name") or "primary"

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("calendar", "v3", http=http)

    if since:
        since = since.to("UTC").isoformat()
    else:
        lookback = get_settings().get("calendar.lookback") or 0
        since = (
            arrow.now()
            .replace(days=-1 * lookback, hour=0, minute=0, second=0, microsecond=0)
            .isoformat()
        )

    timezone = service.settings().get(setting="timezone").execute()["value"]

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
