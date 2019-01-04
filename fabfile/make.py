#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
This module holds the fabric build commands.
'''

# Imports #####################################################################
from __future__ import print_function

from fabric.colors import green
from fabric.api import task

from .helpers import ex


# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUL-2017'


# Globals #####################################################################
def _make_packages():
    print("building source distribution")
    ex('python setup.py bdist_wheel sdist', raise_on_nonzero=True)
    print(green("...OK"))

    print("building universal wheel")
    ex('python setup.py bdist_wheel --universal', raise_on_nonzero=True)
    print(green("...OK"))


@task
def all():
    '''Builds the packages.'''
    ex('rm -rf build dist')
    _make_packages()
    ex('rm -rf build')

    # Report it
    print("packages were built")
    print("...find them in ./dist")
