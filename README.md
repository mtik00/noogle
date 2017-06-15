# Introduction
Controlling your Nest thermostat with Google calendar events

# Requirements

We depend on these things:

*   [python-nest](https://pypi.python.org/pypi/python-nest)
*   [google-api-python-client](https://developers.google.com/google-apps/calendar/quickstart/python)

# Configuration

This application makes use of configuration files to store your specific
settings.  You should probably create your own configuration file:

    python -mgcal_nest --make-user-settings

This will create a file located at `~/.gcal_nest/gcal_nest_settings.ini`.

This folder will also hold the OAuth tokens for both Google and Nest.  You may
wish to change the access bits accordingly.


# Setup

In this example, we're going to be storing some credentials and application setup
in `env/env.bat` (or `env/env.sh` on Linux).

**NOTE** I highly recommend using a virtual environment for this!
1.  Create your application ([configuration file](#Configuration)).
1.  Install `gcal_nest` and its requirements

## Google OAuth 2.0 Setup

1.  Create an application using [Google API](https://console.developers.google.com/flows/enableapi?apiid=calendar&pli=1)
1.  Run the `gcal_nest` setup for Google: `python -m gcal_nest.cli --gcal-setup`
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
1.  Run the `gcal_nest` setup for Nest: `python -m gcal_nest.cli --nest-setup`
1.  If presented with a URL:
    *   Go to the URL
    *   Click the `Accept` button
    *   Copy the *pincode*
    *   Enter the *pincode* in to the prompt
1.  Run the script again to ensure you have the credentials stored (you should not
    be prompted again).

# DSL
`gcal_nest` depends on events in your calendar with specific next.

1.  All events must start with `NEST`
1.  Each piece of the command must be separated with a colon (`:`)
1.  Supported commands are:
    *   `<temp>` : Holds the temperature at the given setpoint (e.g. `nest:65`)
    *   `run` : Run normally until the next even (e.g. `nest:run`)