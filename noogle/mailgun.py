#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
"""
import os
import requests

domain = os.environ.get("MAILGUN_DOMAIN_NAME", 'mailgun-domain-name')
mailgun_api_key = os.environ.get("MAILGUN_API_KEY", "mailgun-api-key")
mailgun_url = f"https://api.mailgun.net/v3/{domain}/messages"
from_address = os.environ.get("MAILGUN_FROM", f"noogle@{domain}")
to_address = os.environ.get("MAILGUN_TO", 'mailgun-to')


def send_message(subject="Notification from noogle", text=None, html=None):
    auth = ("api", mailgun_api_key)

    data = {"from": from_address, "to": [to_address], "subject": subject}

    if text:
        data["text"] = text
    elif html:
        data["html"] = html
    else:
        data["text"] = "unknown message"

    return requests.post(mailgun_url, auth=auth, data=data)
