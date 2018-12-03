#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
"""
import os
import requests

domain = os.environ["MAILGUN_DOMAIN_NAME"]
api = os.environ["MAILGUN_API_KEY"]
mailgun_url = f"https://api.mailgun.net/v3/{domain}/messages"
from_address = os.environ["MAILGUN_FROM"]
to_address = os.environ["MAILGUN_TO"]


def send_message(subject="Notification from gcal_nest", text=None, html=None):
    auth = ("api", api)

    data = {"from": from_address, "to": [to_address], "subject": subject}

    if text:
        data["text"] = text
    elif html:
        data["html"] = html
    else:
        data["text"] = "unknown message"

    return requests.post(mailgun_url, auth=auth, data=data)
