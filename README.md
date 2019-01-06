# TODO

[ ] `circusd` error reporting through `mailgun`
[ ] documentation
[ ] debug mode
[ ] env var setup
[ ] multiple devices/structures?
[ ] all email subjects are "New event scheduled"; not always True
[ ] better delineate between `instance` and `~/.config/noogle` folder
[ ] move app config to yaml (already using it during build anyway)
[ ] have setup create config files and instance folder/files
[ ] add support for 429: Blocked (back off?)
[ ] logging doesn't seem to work

# Introduction
Noogle is a Python3.7 project used to control your Nest thermostat through your Google calendar using events.

# Requirements

*   Python3.7
*   Nest Developer Account (free)
*   Google Developer API Access (free)

See `requirements.txt` for a complete list of requirements.

This service only runs on Python3.7.

# Installation

You can install `noogle` like any other Python package.

1.  Extract the tarball/zip
2.  Run `python3.7 setup.py`

# Configuration

This application makes use of configuration files to store your specific
settings.  You should probably create your own configuration file:

    noogle settings make

This will create a file located at `~/.config/noogle/noogle.ini`.  To change the location of the file, you must set the `SETTINGS_FOLDER` environment variable before making the settings.

This folder will also hold the OAuth tokens for both Google and Nest.  You may
wish to change the access bits accordingly.

# Setup

In this example, we're going to be storing some credentials and application setup
in `instance/env.bat` (or `instance/env.sh` on Linux).

This app is set up in a way that really only works within a virtual environment.  The source ships with a `.envrc` that makes life easier.

1.  Install `direnv` https://direnv.net/
1.  Clone the source to some location:  
    `cd ~ && git clone https://github.com/mtik00/noogle.git`
1.  Create the virtual environment:  
    `cd noogle && direnv allow`
1.  Install `noogle` and its requirements:  
    `pip install -e .[dev] && pip install -r requirements.txt`
1.  Create your application files (*TODO)*:
    `noogle setup init`
1.  Create your Google OAuth credentials
1.  Create your Nest API OAuth credentials
1.  Modify your `site.yaml` file
1.  Modify your `instance/env.sh` file
1.  Test Google calendar integration:  
    `noogle show events`
1.  Test Nest API calendar integration:
    `noogle show structures`
1.  Finally deploy the application:  
    `python deploy`

## Google OAuth 2.0 Setup

1.  Create an application using [Google API](https://console.developers.google.com/flownest-token.jsons/enableapi?apiid=calendar&pli=1)
1.  Download the credentials to `~/.noogle/google_client_secret.json`
1.  Run the `noogle` setup for Google: `noogle setup gcal`
1.  Follow the prompts to allow this computer to access your contacts.
1.  Run the script again to ensure you have the credentials stored (you should not
    be prompted again).

## Nest API Setup

1.  Sign in, or sign up for, a [Nest Developer Accountnest-token.json](https://developers.nest.com/)
1.  Click on 'Create New Product'
1.  Once done, add the `OAuth` parameters to your environment setup file.  For example, add the following to `instance/env.bat`:  
    `set NEST_PRODUCT_ID=ABCDEFG`  
    `set NEST_PRODUCT_SECRET=ABCDEFG`  
1.  Run the `noogle` setup for Nest: `noogle setup nest`
1.  If presented with a URL:
    *   Go to the URL
    *   Click the `Accept` button
    *   Copy the *pincode*
    *   Enter the *pincode* in to the prompt
1.  Run the `noogle show structure` to ensure you have the credentials stored (you should not
    be prompted again).

**NOTE**: If you change the permissions through the Nest API, you must delete `~/.noogle/nest-token.json` and re-run `noogle setup nest`.

# DSL
`noogle` depends on events in your calendar with specific text.  All events should be in the form of:

    nest:<command>:<description>

1.  All events must start with `NEST` (case is not important)
1.  Each part of the command must be separated with a colon (`:`)
1.  Supported commands are:
    *   `away` : Sets the structure to `away` and the thermostat to `eco`
    *   `home` : Sets the structure to `home` and the thermostat to `heat`

A typical command looks like this: `nest:away:Spring Break!`.  The third field
is an optional description.

# Services
There are two service scripts.  One script reads events from your Google calendar, and the other script reads the cache and controls the Nest API.

These two scripts can be run using `circusd` like so:

    circusd --daemon circus.ini

You can control the daemon through the `circusctl` application.  Read more about it here:  https://circus.readthedocs.io/en/latest/

NOTE: For debug purposes, you may want to run `circusd circus.ini` (remove the `--daemon` option to run `circusd` in the foreground)

# Environment Setup
## Fabric
## Dirvnev

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