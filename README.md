# TODO

[ ] mailgun setup
[ ] sqlalchemy?
[ ] deployment
[ ] `circusd` error reporting through `mailgun`
[ ] documentation
[ ] debug mode
[ ] env var setup

# Introduction
This project is used to control your Nest thermostat through your Google calendar using events.

# Requirements

We depend on these things to communicate with Google and Nest APIs:

*   [python-nest](https://pypi.python.org/pypi/python-nest)
*   [google-api-python-client](https://developers.google.com/google-apps/calendar/quickstart/python)

See `requirements.txt` for a complete list of requirements.

# Configuration

This application makes use of configuration files to store your specific
settings.  You should probably create your own configuration file:

    python -mgcal_nest --make-user-settings

This will create a file located at `~/.gcal_nest/gcal_nest_settings.ini`.  To change the location of the file, you must set the `SETTINGS_FOLDER` environment variable.

This folder will also hold the OAuth tokens for both Google and Nest.  You may
wish to change the access bits accordingly.


# Setup

In this example, we're going to be storing some credentials and application setup
in `env/env.bat` (or `env/env.sh` on Linux).

**NOTE** I highly recommend using a virtual environment for this!
1.  Install `gcal_nest` and its requirements
1.  Create your application ([configuration file](#Configuration)).

## Google OAuth 2.0 Setup

1.  Create an application using [Google API](https://console.developers.google.com/flows/enableapi?apiid=calendar&pli=1)
1.  Download the credentials to `~/.gcal_nest/google_client_secret.json`
1.  Run the `gcal_nest` setup for Google: `gcal_nest setup gcal`
1.  Follow the prompts to allow this computer to access your contacts.
1.  Run the script again to ensure you have the credentials stored (you should not
    be prompted again).

## Nest API Setup

1.  Sign in, or sign up for, a [Nest Developer Account](https://developers.nest.com/)
1.  Click on 'Create New Product'
1.  Once done, add the `OAuth` parameters to your environment setup file.  For example, add the following to `env/env.bat`:  
    `set NEST_PRODUCT_ID="ABCDEFG"`  
    `set NEST_PRODUCT_SECRET="ABCDEFG"`  
    Alternatively, you may insert these into `~/.gcal_nest/gcal_nest_settings.ini`
1.  Run the `gcal_nest` setup for Nest: `gcal_nest setup nest`
1.  If presented with a URL:
    *   Go to the URL
    *   Click the `Accept` button
    *   Copy the *pincode*
    *   Enter the *pincode* in to the prompt
1.  Run the script again to ensure you have the credentials stored (you should not
    be prompted again).

**NOTE**: If you change the permissions through the Nest API, you must delete `~/.gcal_nest/nest-token.json` and re-run `gcal_nest setup nest`.

# DSL
`gcal_nest` depends on events in your calendar with specific text.  All events should be in the form of:

    nest:<command>:<description>

1.  All events must start with `NEST`
1.  Each piece of the command must be separated with a colon (`:`)
1.  Supported commands are:
    *   `away` : Sets the structure to `away` and the thermostat to `eco`
    *   `home` : Sets the structure to `home` and the thermostat to `heat`

A typical command looks like this: `nest:home:Spring Break!`.  The third field
is an optional description.

# Services
There are two service scripts.  One script reads event from your Google calendar, and the other script reads the cache and controls the Nest API.

These two scripts can be run using `circusd` like so:

    circusd --daemon circus.ini

You can control the daemon through the `circusctl` application.  Read more about it here:  https://circus.readthedocs.io/en/latest/

NOTE: For debug purposes, you may want to run `circusd circus.ini` (remove the `--daemon` option to run `circusd` in the foreground)