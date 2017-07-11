#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module manages the version info.
'''

# Imports #####################################################################
import os
import re

# import pypandoc
from fabric.api import task

from .constants import VERSION_FILE, BASE_DIR
from .helpers import ex, true


# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '11-JUL-2017'


# Globals #####################################################################
RE_VERSION = re.compile(
    '^__version__\s*=\s*[\'"](?P<version>.*?)[\'"]\s*?^', re.MULTILINE)


def _get_version(
    python_file=VERSION_FILE,
    regex='(__version__ = ["\'])(?P<version>\d+\.\d+.*)(["\'])',
    display='n'
):
    file_text = open(python_file).read()
    match = re.search(regex, file_text)
    if not match:
        raise Exception("Can't get build version from [%s]" % python_file)

    if true(display):
        print(match.group("version"))

    return match.group("version")


@task
def get(python_file=VERSION_FILE, regex='(__version__ = ["\'])(?P<version>\d+\.\d+.*)(["\'])'):
    '''Gets the current version of SVT-HTTP'''
    return _get_version(python_file, regex, display='y')


@task
def rev():
    """Increases the 'minor' version number by 1"""
    from .git import push_origin

    text = open(VERSION_FILE).read()
    whole, ver = re.search("^(__version__\s+=\s+['\"](.*?)['\"]\s*)$", text, re.MULTILINE).groups()
    major, minor, patch = ver.split('.', 2)

    # Remove any alpha/beta/etc characters.
    major = re.search('(\d+)', major).group(0)
    minor = re.search('(\d+)', minor).group(0)

    new_minor = str(int(minor) + 1)

    # NOTE: When reving minor, it's customary to set patch to "0"
    new_ver = ".".join([major, new_minor, "0"])

    print("Old version number is [%s]" % ver)
    print("New version number is [%s]" % new_ver)
    val = raw_input("OK [Yn]? ")
    while "y" not in val.strip().lower():
        new_ver = raw_input("Enter new version: ")
        print("Using new version [%s]" % new_ver)
        val = raw_input("OK [Yn]? ")

    text = text.replace(ver, new_ver)
    with open(VERSION_FILE, "wb") as fh:
        fh.write(text)

    val = raw_input("Copy to setup.py [Yn]? ")
    if "y" in val.strip().lower():
        setup()

    val = raw_input("Commit [Yn]? ")
    if "y" in val.strip().lower():
        ex(["git", "add", VERSION_FILE])
        ex(["git", "commit", '-m', "INTERNAL: reving version number to [%s]" % new_ver])

        val = raw_input("Push [Yn]? ")
        if true(val):
            push_origin()


@task
def setup():
    '''Update the version in `setup.py` to the module's version.'''
    setupfile = os.path.join(BASE_DIR, 'setup.py')
    lib_ver = _get_version()

    with open(setupfile) as fh:
        text = fh.read()

    text = re.sub('version="0.0.0",', 'version="%s",' % lib_ver, text)
    text = re.sub('download/v0.0.0/"', 'download/v%s/"' % lib_ver, text)
    text = re.sub('gcal_nest-0.0.0.tar.gz', 'gcal_nest-%s.tar.gz' % lib_ver, text)

    # readme = os.path.join(BASE_DIR, 'README.md')
    # output = pypandoc.convert_file(readme, 'rst')
    # print output

    with open(setupfile, 'wb') as fh:
        fh.write(text)
