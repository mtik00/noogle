#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module has the class used to control the Nest thermostat.
'''

# Imports #####################################################################

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '07-JUN-2017'


# Globals #####################################################################
COMMANDS = {
    ":ON": 1
}


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
