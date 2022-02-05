#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
from typing import Sequence

import requests
from google_auth_oauthlib.flow import InstalledAppFlow

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

base_api_url = (
    "https://smartdevicemanagement.googleapis.com/v1/enterprises/{product_id}"
)


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
        credentials = flow.run_console()

    # Save the access token
    access_token.write_text(credentials.to_json())

    return credentials


def get(url, token: str, product_id: str):
    """
    Use the token to request the provided URL.
    """
    auth = "Bearer ".encode("ascii") + token.encode("ascii", "ignore")
    headers = {"authorization": auth, "content-type": "application/json"}

    response = requests.get(
        base_api_url.format(product_id=product_id) + url,
        headers=headers,
        allow_redirects=False,
    )

    if response.status_code == 307:
        response = requests.get(
            response.headers["Location"], headers=headers, allow_redirects=False
        )

    response.raise_for_status()

    return response.json()


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    if len(sys.argv) != 2:
        print("ERROR: must enter the Nest product ID")
        return

    oauth_token = Path(".secrets", "tokens", "nest-oauth-client-secret.json")
    access_token = Path(".secrets", "tokens", "tmp-nest-access-token.json")
    scopes = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/sdm.service",
    ]

    creds = login(oauth_token, access_token, scopes)
    data = get(url="/devices", token=creds.token, product_id=sys.argv[1])
    print(json.dumps(data, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
