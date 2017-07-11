#!/usr/bin/env python2.7
# coding: utf-8
###############################################################################
#                                                                             #
#  Copyright (C) 2015-2017 Broadcom Ltd.  All rights reserved.                #
#                                                                             #
###############################################################################
'''
This module is used to provide compatability functions/objects between Python
2 and Python 3.
'''

# Imports #####################################################################
import sys

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUL-2017'
__license__ = 'Proprietary'


# Globals #####################################################################
if sys.version_info.major == 2:
    MY_BASESTRING = basestring
else:
    MY_BASESTRING = str


def get_input(prompt):
    '''
    Python 2 and 3 compatible way of getting user input.
    '''
    if sys.version_info.major == 2:
        return raw_input(prompt)
    else:
        return input(prompt)
