#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module holds the interface to Google calendar.
'''

# Imports #####################################################################
# from .settings import settings
import os
import argparse
import datetime
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from .settings import USER_FOLDER

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '08-JUN-2017'


# Globals #####################################################################
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'env/google_client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials(noauth_local_webserver=False):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    NOTE: This was modified from
    https://developers.google.com/google-apps/calendar/quickstart/python

    Returns:
        Credentials, the obtained credential.
    """
    if not os.path.exists(USER_FOLDER):
        os.makedirs(USER_FOLDER)
    credential_path = os.path.join(
        USER_FOLDER, 'google-calendar.json')

    if noauth_local_webserver:
        flags = argparse.ArgumentParser(
            parents=[tools.argparser]).parse_args(['--noauth_local_webserver'])
    else:
        flags = None

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def setup(noauth_local_webserver=False):
    '''
    Set up your credentials for access to google calendar.
    '''
    get_credentials(noauth_local_webserver=noauth_local_webserver)
    events = get_next_events()
    if not events:
        print('No upcoming events found.')

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def get_next_events(max_results=10, q='nest'):
    '''
    Returns a list of events filtered by ``q``.

    :param int max_results: The maximum number of results to return
    :param str q: This is the "advanced search syntax" item
    '''
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary', timeMin=now, maxResults=max_results,
        singleEvents=True, orderBy='startTime', q=q).execute()

    events = events_result.get('items', [])
    return events
