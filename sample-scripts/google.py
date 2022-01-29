#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
from pathlib import Path
from typing import Sequence

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def login(oauth_token: Path, access_token: Path, scopes: Sequence[str]) -> Credentials:
    credentials = None

    if not oauth_token.exists():
        raise Exception(
            "You must download your Google OAuth token file to:", str(oauth_token)
        )

    # Read previous auth info
    if access_token.exists():
        credentials = Credentials.from_authorized_user_file(access_token, scopes)

    # If have expired credentials, refresh them.  Otherwise, re-run authorization.
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials:
        flow = InstalledAppFlow.from_client_secrets_file(
            oauth_token,
            scopes,
        )
        credentials = flow.run_local_server(port=0)

    # Save the access token
    access_token.write_text(credentials.to_json())

    return credentials


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    oauth_token = Path(".secrets", "tokens", "calendar-oauth-client-secret.json")
    access_token = Path(".secrets", "tokens", "tmp-calendar-access-token.json")
    scopes = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/sdm.service",
    ]

    creds = login(oauth_token, access_token, scopes)
    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print("An error occurred: %s" % error)


if __name__ == "__main__":
    main()
