#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
noogle management script
'''

# Imports #####################################################################

from fabric.api import env

# Trigger fabric's submodule parsing
from .make import _make_packages  # noqa: F401
from .ver import _get_version  # noqa: F401

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUL-2017'

# Fabric environment setup ####################################################
env.colorize_errors = True


# Globals #####################################################################
