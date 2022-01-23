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

## Google OAuth 2.0 Setup

1.  Create an application using [Google API](https://console.developers.google.com/flownest-token.jsons/enableapi?apiid=calendar&pli=1)
1.  Download the credentials to `~/.noogle/google_client_secret.json`
1.  Run the `noogle` setup for Google: `noogle setup gcal`
1.  Follow the prompts to allow this computer to access your contacts.
1.  Run the script again to ensure you have the credentials stored (you should not
    be prompted again).

## Nest API Setup

1.  Sign in, or sign up for, a [Nest Developer Account](https://developers.nest.com/)
1.  Click on 'Create New Product'
1.  Once done, add the `OAuth` parameters to your environment setup file.  For example, add the following to `${SECRETS_FOLDER}/env.bat`:  
    `export NEST_PRODUCT_ID=ABCDEFG`  
    `export NEST_PRODUCT_SECRET=ABCDEFG`  
1.  Run the `noogle` setup for Nest: `noogle setup nest`
1.  If presented with a URL:
    *   Go to the URL
    *   Click the `Accept` button
    *   Copy the *pincode*
    *   Enter the *pincode* in to the prompt
1.  Run the `noogle show structures` to ensure you have the credentials stored (you should not be prompted again).

**NOTE**: If you change the permissions through the Nest API, you must delete `${SECRETS_FOLDER}/tokens/nest-token.json` and re-run `noogle setup nest`.

# Docker / docker-compose

You can build and run the service using `docker-compose`.

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
