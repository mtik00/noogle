#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
"""
from typing import Optional

import requests
from pydantic import SecretStr

from .settings import settings


def send_message(
    subject: str = "Notification from noogle",
    text: str = None,
    html: str = None,
    domain: str = None,
    api_key: Optional[SecretStr] = None,
    to_address: str = None,
    from_address: str = None,
):
    if not (text or html):
        raise ValueError("Must pass both/either of `text` and `html`")

    domain = domain or settings.mailgun.domain_name
    api_key = api_key or settings.mailgun.api_key
    to_address = to_address or settings.mailgun.to_address
    from_address = from_address or settings.mailgun.from_address

    data = {
        "from": from_address,
        "to": [to_address],
        "subject": subject,
        "text": text,
        "html": html,
    }

    auth = ("api", api_key.get_secret_value())
    mailgun_url = f"https://api.mailgun.net/v3/{domain}/messages"
    response = requests.post(mailgun_url, auth=auth, data=data)
    response.raise_for_status()
    return response
