#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module holds the interface to Google calendar.
"""

# Imports #####################################################################
import os
import sys
import argparse
import httplib2
from pathlib import Path

import arrow
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.errors import HttpError

from .settings import settings
from .models import Event
from .helpers import print_log


# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "08-JUN-2017"


# Globals #####################################################################
SCOPES = "https://www.googleapis.com/auth/calendar.readonly"
CLIENT_SECRET_FILE = Path(settings.general.token_folder, "google-client-secret.json")
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
        print_log("ERROR: Google client secrect not found at: %s" % CLIENT_SECRET_FILE)
        print_log("...Download the JSON credentials from:")
        print_log("...https://console.developers.google.com/apis/credentials")
        print_log("...and put them here: %s" % CLIENT_SECRET_FILE)
        print_log("Dont forget to rename the file!")
        sys.exit(1)

    if not os.path.exists(TOKEN_FOLDER):
        os.makedirs(TOKEN_FOLDER)
    credential_path = os.path.join(TOKEN_FOLDER, "google-calendar.json")

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
        print_log("Storing credentials to " + credential_path)
    return credentials


def setup(auth_local_webserver=False):
    """
    Set up your credentials for access to google calendar.
    """
    noauth_local_webserver = not auth_local_webserver
    get_credentials(noauth_local_webserver=noauth_local_webserver)
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

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("calendar", "v3", http=http)

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
