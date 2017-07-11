#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
This modules holds management helper functions.
'''

# Imports #####################################################################
import os
import re
import subprocess

from .constants import VERSION_FILE

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUN-2017'


# Globals #####################################################################
def true(value):
    '''
    Returns a boolean value representing the input.

    True is some value like: ['y', 1, True]
    '''
    if isinstance(value, bool):
        return value
    elif isinstance(value, basestring):
        return value.lower().startswith('y')

    return bool(value)


def ex(command, cwd=None, shell=None, raise_on_nonzero=False):
    """Execute a command and return the output.  This will raise an Exception if
    the return code is non-zero.

    :param str/list command: Either a string or a list of arguments.
    :param bool shell: If None, "shell" will be determined by the type of `command`
        (str -> shell=True; list -> shell=False)
    :param bool raise_on_nonzero: Raise an exception if the return code of the
        process is not zero.
    :returns: tuple(text, returncode)
    """
    shell = shell if (shell is not None) else (type(command) is not list)

    p = subprocess.Popen(command, shell=shell, cwd=cwd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output, _ = p.communicate()

    if p.returncode and raise_on_nonzero:
        raise Exception("command failed: %s" % output)

    return (output, p.returncode)


def get_version():
    '''
    Returns the module's version.
    '''
    with open(VERSION_FILE) as fh:
        text = fh.read()

    match = re.search(
        '^__version__\s*=\s*[\'"](?P<version>.*?)[\'"]',
        text, re.MULTILINE)

    return match.group('version')
