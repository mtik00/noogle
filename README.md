# Introduction
Controlling your Nest thermostat with Google calendar events


## Setup

*   Nest developer API
*   [Google API](https://console.developers.google.com/flows/enableapi?apiid=calendar&pli=1)

## Requirments

We depend on these things:

*   [python-nest](https://pypi.python.org/pypi/python-nest)
*   [google-api-python-client](https://developers.google.com/google-apps/calendar/quickstart/python)

# DSL
`gcal_nest` depends on events in your calendar with specific next.

1.  All events must start with `NEST`
1.  Each piece of the command must be separated with a colon (`:`)
1.  Supported commands are:
    *   `HOLD` : Holds the current setpoint
    *   `HOLD:<temp>` : Holds the temperature at the given setpoint
    *   `RUN` : Run normally until the next even