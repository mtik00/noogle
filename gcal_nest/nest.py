#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module has the class used to control the Nest thermostat.
"""

# Imports #####################################################################
from __future__ import print_function, absolute_import
import os
import time
import nest

from .compat import prompt
from .settings import get_settings, USER_FOLDER
from .models import Action


# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "07-JUN-2017"


# Globals #####################################################################
def setup(ctx):
    """
    Test or create the Nest API OAuth token.
    """
    napi = get_nest_api(ctx)

    for structure in napi.structures:
        print("Structure %s" % structure.name)
        print("    Away: %s" % structure.away)
        print("    Devices:")

        for device in structure.thermostats:
            print("        Device: %s" % device.name)
            print("            Temp: %0.1f" % device.temperature)


def get_nest_api(ctx, refresh=False):
    if ctx.napi and (not refresh):
        return ctx.napi

    settings = get_settings()
    client_id = settings.get("nest.product-id") or os.environ.get("NEST_PRODUCT_ID")
    client_secret = settings.get("nest.product-secret") or os.environ.get(
        "NEST_PRODUCT_SECRET"
    )

    if not (client_id and client_secret):
        raise ValueError(
            "You must enter your Nest product ID and product "
            "secret!  See setup instructions."
        )

    if not os.path.isdir(USER_FOLDER):
        os.makedirs(USER_FOLDER)

    access_token_cache_file = os.path.join(USER_FOLDER, "nest-token.json")
    napi = nest.Nest(
        client_id=client_id.strip('"').strip("'"),
        client_secret=client_secret.strip('"').strip("'"),
        access_token_cache_file=access_token_cache_file,
    )

    if napi.authorization_required:
        print("Go to " + napi.authorize_url + " to authorize, then enter PIN below")
        pin = prompt("PIN: ")
        napi.request_token(pin)

    ctx.napi = napi

    return napi


def get_structures(napi):
    return napi.structures


def get_napi_structure(ctx, napi=None):
    """
    Returns the Structure object that matches the settings
    """
    napi = napi or get_nest_api(ctx)

    structure_name = ctx.project_settings.get("nest.structure").lower()
    structure = None
    if structure_name:
        structure = next(
            (x for x in napi.structures if x.name.lower() == structure_name), None
        )
    elif len(napi.structures):
        structure = napi.structures[0]

    if not structure:
        raise ValueError("Nest structure not found")

    return structure


def get_napi_thermostat(ctx, napi=None):
    napi = get_nest_api(ctx)

    structure = get_napi_structure(ctx, napi)

    thermostat_name = ctx.project_settings.get("nest.device")
    thermostat = None
    if thermostat_name:
        thermostat = next(
            (
                x
                for x in structure.thermostats
                if x.name.lower() == thermostat_name.lower()
            ),
            None,
        )
    elif len(structure.thermostats):
        thermostat = structure.thermostats[0]

    if not thermostat:
        raise ValueError("Nest device not found")

    return thermostat


def get_thermostat(ctx):
    """
    Gets the current temperature of the Nest device
    """
    napi = get_nest_api(ctx)
    return get_napi_thermostat(ctx, napi)


def do_away(ctx):
    napi = get_nest_api(ctx)
    structure = get_napi_structure(ctx, napi)

    print("Structure: %s" % structure.name)

    if structure.away != "away":
        structure.away = "away"
    else:
        print('...already in "away" mode')

    if structure.thermostats[0].mode != "eco":
        structure.thermostats[0].mode = "eco"
        print('...changed mode to "eco"')


def do_home(ctx):
    napi = get_nest_api(ctx)
    structure = get_napi_structure(ctx, napi)

    print("Structure: %s" % structure.name)

    if structure.away != "home":
        structure.away = "home"
    else:
        print('...already in "home" mode')

    if structure.thermostats[0].mode != "heat":
        structure.thermostats[0].mode = "heat"
        print('...changed mode to "heat"')


def verify(ctx, event):
    """
    Verify the event actually occurred.
    """
    errors = []
    napi = get_nest_api(ctx)
    structure = get_napi_structure(ctx, napi)

    if event.action == Action.home:
        away = "home"
        mode = "heat"
    else:
        away = "away"
        mode = "eco"

    if structure.away != away:
        errors.append(f"Structure is not marked as {away}!")

    if structure.thermostats[0].mode != mode:
        errors.append(f"Thermostat mode is not set to {mode}!")

    if errors:
        message = "\n".join(errors)
        raise Exception(message)


def do_event(ctx, event):
    action_map = {Action.away.value: do_away, Action.home.value: do_home}

    func = action_map.get(event.action.value, None)
    if func:
        func(ctx)

        print("...waiting 30s before verification")
        time.sleep(30)

        verify(ctx, event)
    else:
        raise Exception("Unkown event action: {!r}".format(event.action))


class NestControl(object):
    """
    This object interfaces with the Nest API to control a Nest thermostat.
    """

    def __init__(self):
        pass

    def do_command(self, command):
        """
        Performs a command according to the specification.
        """
        # NEST:HOME
        # NEST:AWAY

        # Future reference:
        # NEST:HOLD:##:#d (hold temp for # days, then call NEST:OFF)
        # NEST:HOLD:##:#d:## (hold temp for # days, then set to ##)
        # NEST:OFF (set to default eco)
        pass