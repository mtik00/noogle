#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
from pathlib import Path
from typing import Sequence, Optional

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from .settings import settings


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/sdm.service",
]


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


def get_credentials(
    oauth_token: Optional[Path] = None,
    access_token: Optional[Path] = None,
    scopes: Sequence[str] = SCOPES,
):
    if not oauth_token:
        oauth_token = settings.general.token_folder / "noogle-oauth-token.json"

    if not access_token:
        access_token = settings.general.token_folder / "tmp-access-token.json"

    return login(oauth_token, access_token, scopes)
