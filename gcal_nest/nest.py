#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module has the class used to control the Nest thermostat.
'''

# Imports #####################################################################
from __future__ import print_function, absolute_import
import os

import nest

from .settings import get_settings, USER_FOLDER

try:
    input = raw_input
except NameError:
    pass

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '07-JUN-2017'


# Globals #####################################################################
def setup(ctx):
    '''
    Test or create the Nest API OAuth token.
    '''
    napi = get_nest_api(ctx)

    for structure in napi.structures:
        print ('Structure %s' % structure.name)
        print ('    Away: %s' % structure.away)
        print ('    Devices:')

        for device in structure.thermostats:
            print ('        Device: %s' % device.name)
            print ('            Temp: %0.1f' % device.temperature)


def get_nest_api(ctx):
    if ctx.napi:
        return ctx.napi

    settings = get_settings()
    client_id = settings.get('nest.product-id') or os.environ.get('NEST_PRODUCT_ID')
    client_secret = settings.get('nest.product-secret') or os.environ.get('NEST_PRODUCT_SECRET')

    if not(client_id and client_secret):
        raise ValueError(
            "You must enter your Nest product ID and product "
            "secret!  See setup instructions.")

    if not os.path.isdir(USER_FOLDER):
        os.makedirs(USER_FOLDER)

    access_token_cache_file = os.path.join(USER_FOLDER, 'nest-token.json')
    napi = nest.Nest(
        client_id=client_id.strip('"').strip("'"),
        client_secret=client_secret.strip('"').strip("'"),
        access_token_cache_file=access_token_cache_file)

    if napi.authorization_required:
        print('Go to ' + napi.authorize_url + ' to authorize, then enter PIN below')
        pin = input("PIN: ")
        napi.request_token(pin)

    ctx.napi = napi

    return napi


def get_structures(napi):
    return napi.structures


def get_napi_thermostat(ctx, napi=None):
    napi = get_nest_api(ctx)

    structure_name = ctx.project_settings.get('nest.structure')
    structure = None
    if structure_name:
        structure = next((x for x in napi.structures if x.name.lower() == structure_name), None)
    elif len(napi.structures):
        structure = napi.structures[0]

    if not structure:
        raise ValueError("Nest structure not found")

    thermostat_name = ctx.project_settings.get('nest.device')
    thermostat = None
    if thermostat_name:
        thermostat = next((x for x in structure.thermostats if x.name.lower() == thermostat_name.lower()), None)
    elif len(structure.thermostats):
        thermostat = structure.thermostats[0]

    if not thermostat:
        raise ValueError("Nest device not found")

    return thermostat


def get_thermostat(ctx):
    '''
    Gets the current temperature of the Nest device
    '''
    napi = get_nest_api(ctx)
    return get_napi_thermostat(ctx, napi)


class NestControl(object):
    '''
    This object interfaces with the Nest API to control a Nest thermostat.
    '''
    def __init__(self):
        pass

    def do_command(self, command):
        '''
        Performs a command according to the specification.
        '''
        # NEST:ON (also set to 'Home')
        # NEST:HOLD:##
        # NEST:HOLD:##:#d (hold temp for # days, then call NEST:OFF)
        # NEST:HOLD:##:#d:## (hold temp for # days, then set to ##)
        # NEST:OFF (set to default eco)
        pass
