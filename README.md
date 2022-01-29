# TODO

- [ ] `circusd` error reporting through `mailgun`
- [ ] documentation
- [ ] debug mode (Nest dev?)
- [ ] env var setup
- [ ] multiple devices/structures?
- [ ] move app config to yaml/toml (already using it during build anyway)
- [ ] add support for 429: Blocked (back off?)
- [ ] stop trying failed commands after X time
 
# Introduction
Noogle is a Python3.7+ project used to control your Nest thermostat through your Google calendar using events.

# Requirements

*   Python3.7+
*   Nest Developer Account (free)
*   Google Developer API Access (free)

See `pyproject.toml` for a complete list of Python requirements.

**This service only runs on Python3.7+**

# Setup

We're using docker-compose and local files for this setup.  You should clone this repo.  It will make things a lot easier.

After cloning the repo, run this script to create a virtual environment and create the basic folder structure:
```
python3 -m venv --copies .venv && \
source .venv/bin/activate && \
./.venv/bin/pip install --upgrade pip poetry && \
./.venv/bin/poetry install && \
python ./skel.py
```
Get your tokens from both Google and Nest an place them in `.secrets/tokens`.

Change the values in `.env` as needed.

Initialize the database with:
```
python -m noogle init db
```

# Authentication

These directions create separate credentials between Google Calendar and Nest Device Access.  This allows you to use different accounts as you see fit (e.g. you use a different account for Calendar than you do for Nest).

This is the worst part if you are using multiple Google accounts.

## Google OAuth 2.0 Setup -- Calendar

1   Create a new GCP project called `noogle`: https://console.cloud.google.com/
1.  Enable the "Google Calendar" and "Smart Device Management" APIs to  your project: https://console.cloud.google.com/apis/library
1.  Configure the OAuth consent screen: https://console.cloud.google.com/apis/credentials/consent
    - Choose "External" for User Type
    - App name: <domain name> -- noogle
    - Select your email for _User support email_
    - Add your domain for _Authorized domains_
    - Enter your email for _Developer contact information_
    - Hit "Save and continue"
    - Add scopes:
        * Google Calendar API: .../auth/calendar.readonly
        * Smart Device Management API: .../auth/sdm.service
    - Hit "Save and continue"
    - Add your user as a _Test user_
    - Hit "Save and continue"
1.  Create a google new credentials: https://console.cloud.google.com/apis/credentials
    - Click "CREATE CREDENTIALS"
    - Select "OAuth Client ID"
    - Select "Desktop app" for _Application type_
    - Select a name for it
    - Click "Create"
1.  Download the OAuth 2.0 Client `json` file to `.secrets/tokens/calendar-oauth-client-secret.json`
1.  Set `.env` NOOGLE_CALENDAR__TOKEN_FILE to `.secrets/tokens/calendar-oauth-client-secret.json`
1.  Run the sample script: `python sample-scripts/google.py`
1.  Visit the URL to authorize the application
1.  You should see a message like "Getting upcoming 10 events"

## Google OAuth 2.0 Setup -- Nest

If your "main" Calendar is tied to the same account as your Nest account, you should use the same credentials as you created above for Calendar.  Simply set `NOOGLE_NEST__TOKEN_FILE` to `.secrets/tokens/calendar-oauth-client-secret.json`.

These directions are the case where the calendar you use day-to-day is a different Google account than your Nest account.  This is normal if your main Google account is a Workspace account (custom domain name using Gmail).  As of 2022-JAN, you cannot migrate your Nest Account to a Google Workspace account... bummer.

It's easiest to follow these directions by using an incognito window logged in to your Nest account.

These are abreviate instructions.  See the instructions for Calendar above for more in-depth steps.

1.  Make sure you Nest account has been migrated to Google.
    WARNING: You can't use a GSuite account for this as of 2022-JAN.  You must use a `gmail.com` account.
1   Create a new GCP project: https://console.cloud.google.com/ called `noogle`
1.  Enable the "Smart Device Management" API https://console.cloud.google.com/apis/library
1.  Configure the OAuth consent screen: https://console.cloud.google.com/apis/credentials/consent
1.  Create a google a new _OAuth 2.0 Client ID_ https://console.cloud.google.com/apis/credentials
1.  Download the OAuth 2.0 Client `json` file to `.secrets/tokens/nest-oauth-client-secret.json`
1.  Set `.env` NOOGLE_NEST__TOKEN_FILE to `.secrets/tokens/nest-oauth-client-secret.json`
1.  Create a new "Nest Device Access" project: https://console.nest.google.com/device-access/project-list.  This costs US$5 as of 2022-JAN.
1.  Use your oauth client ID and your Nest device project ID and follow these directions: https://developers.google.com/nest/device-access/authorize
    NOTE: You need to follow those and allow each "structure"
1.  Run the sample script: `python sample-scripts/nest.py` with your Nest Project ID
1.  Visit the URL to authorize the application
1.  You should see a dump of your Nest devices

# Docker / docker-compose

You can build and run the service using `docker-compose`.

It's "best" to run docker as your user to keep the permissions in the bind mounts.  We're using `1000` here.  You can find your user ID by running `echo $UID` in your shell.

NOTE: Normally `$UID` isn't an actual environment variable.  You probably can't use `$UID` in your `docker-compose run` command.

For example:
```
/usr/local/bin/docker-compose pull && \
/usr/local/bin/docker-compose run --rm --user 1000 noogle service both --poll 5
 ```

or run it on a cron schedule:
```
*/5 * * * * cd /home/ubuntu/code/noogle && /usr/local/bin/docker-compose run --rm --user 1000 noogle service both --once
```

NOTE: ymmv: `sudo setfacl --modify user:<user name or ID>:rw /var/run/docker.sock`

# Configuration

All application configuration is handled by environment variables and an optional _dotenv_ file.

You should have a sample `.env` file that was generated when you ran `python skel.py`.

You can read more about how settings work here: https://pydantic-docs.helpmanual.io/usage/settings/

# DSL
`noogle` depends on events in your calendar with specific text.  All events should be in the form of:

    nest:<command>:<description>

1.  All events must start with `NEST` (case is not important)
1.  Each part of the command must be separated with a colon (`:`)
1.  Supported commands are:
    *   `away` : Sets the structure to `away` and the thermostat to `eco`
    *   `home` : Sets the structure to `home` and the thermostat to the previous mode (or _heat_ in the winter)

A typical command looks like this: `nest:away:Spring Break!`.  The third field
is an optional description.

# Theory
Here's how I think this should all work.  The bulk of the logic should be in the calendar service, since we need to figure out upcoming events, deleted events, etc.  The nest service only needs to the check the DB for something to do at that exact moment.

*   The calendar service should check for events every hour
*   If events are found that don't exist already, add them to the DB
*   If we have *waiting* events in the DB that aren't found, mark them as missing
*   The Nest service should check for events in the DB every 5 minutes
*   If it's time for an event, do it, mark the event done, and send an email

# Rate Limits
You should not test the service on live hardware.  Nest rate-limits requests.  You'll begin to get `429 Too Many Requests` returns from the API.  The data might look something like this:

    {'error': 'blocked',
    'instance': '...',
    'message': 'blocked',
    'type': 'https://developer.nest.com/documentation/cloud/error-messages#blocked'}
