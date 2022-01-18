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

See `requirements.txt` for a complete list of Python requirements.

**This service only runs on Python3.7+**

# Setup

In this example, we're going to be storing some credentials and application setup
in `${SECRETS_FOLDER}/env.bat` (or `${SECRETS_FOLDER}/env.sh` on Linux).

This app is set up in a way that really only works within a virtual environment.  The source ships with a `.envrc` that makes life easier.

1.  Install `direnv` https://direnv.net/
1.  Clone the source to some location:  
    `cd ~ && git clone https://github.com/mtik00/noogle.git`
1.  Create the virtual environment:  
    `cd noogle && direnv allow`
1.  Install `noogle` and its requirements:  
    `pip install -e .[dev] && pip install -r requirements.txt`
1.  Create your application files (*TODO)*:
    `noogle init all`
1.  Create your Google OAuth credentials
1.  Create your Nest API OAuth credentials
1.  Modify your `${SECRETS_FOLDER}/config/deploy.yaml` file (if needed)
1.  Modify your `${SECRETS_FOLDER}/env.sh` file
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

This application makes use of configuration files to store your specific
settings.  You should probably create your own configuration file:

    noogle settings make

This will create a file located at `${SECRETS_FOLDER}/config/noogle.ini`.  To change the location of the file, you must set the `SETTINGS_FOLDER` environment variable before making the settings.

# DSL
`noogle` depends on events in your calendar with specific text.  All events should be in the form of:

    nest:<command>:<description>

1.  All events must start with `NEST` (case is not important)
1.  Each part of the command must be separated with a colon (`:`)
1.  Supported commands are:
    *   `away` : Sets the structure to `away` and the thermostat to `eco`
    *   `home` : Sets the structure to `home` and the thermostat to the previous mode

A typical command looks like this: `nest:away:Spring Break!`.  The third field
is an optional description.

# Services
There are two service scripts.  One script reads events from your Google calendar, and the other script reads the cache and controls the Nest API.

These two scripts can be run using `circusd` like so:

    circusd circus.ini

# Environment Setup
## Fabric
I use *Fabric* to deploy this application to my VPS.  If you are running everything directly on your VPS, you can ignore this section.

`deploy.py` depends on these environment variable being set:
*   `NOOGLE_APP_HOST`: This is the hostname of where the app will be deployed
*   `NOOGLE_APP_HOME_FOLDER`: This is the absolute path to the cloned folder.
*   `NOOGLE_VENV_ACTIVATE_COMMAND`: This is the command you use to activate your virtual environment.  Optional.

## Dirvnev
This project ships with a `.envrc` file.  This file is read by `Direnv` to control creation of the virtual environment used by the app.

Part of `.envrc` is sourcing `${SECRETS_FOLDER}/env.sh` in order to set up the application variables as needed.  You *must* export the following shell variables:
*   `NEST_PRODUCT_ID`: Get this from your Nest developer account
*   `NEST_PRODUCT_SECRET`: Get this from your Nest developer account
*   `MAILGUN_API_KEY`: Get this from your Mailgun account
*   `MAILGUN_DOMAIN_NAME`: Get this from your Mailgun account
*   `MAILGUN_FROM`: The `from` address for the emails sent by the app
*   `MAILGUN_TO`: The `to` address where emails will be sent

If you are deploying to a different server, also see [Fabric](#Fabric) setup.

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
