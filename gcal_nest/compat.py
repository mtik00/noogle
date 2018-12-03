#!/usr/bin/env python2.7
# coding: utf-8
###############################################################################
#                                                                             #
#  Copyright (C) 2015-2017 Broadcom Ltd.  All rights reserved.                #
#                                                                             #
###############################################################################
"""
This module is used to provide compatability functions/objects between Python
2 and Python 3.

This is basically a rip-off of six.py, just a lot smaller.
"""

# Imports #####################################################################
import sys

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUL-2017"
__license__ = "Proprietary"


# Globals #####################################################################
PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

if PY3:
    string_types = (str,)
    prompt = input
else:
    string_types = (basestring,)
    prompt = raw_input
