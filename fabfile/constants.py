#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
This module holds the fabric constants
'''

# Imports #####################################################################
import os
import sys

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'

# Globals #####################################################################
HIDE = True
(IS_WIN, IS_LIN) = ('win' in sys.platform, 'lin' in sys.platform)
THIS_DIR = os.path.dirname(__file__)
VERSION_FILE = os.path.join(THIS_DIR, '..', 'gcal_nest', '__init__.py')
DIST_DIR = os.path.join(THIS_DIR, '..', 'dist')
BUILD_DIR = os.path.join(THIS_DIR, '..', 'build')
BASE_DIR = os.path.join(THIS_DIR, '..')

UPSTREAM_REPO = "git@github.com:mtik00/gcal_nest.git"
