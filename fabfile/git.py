#!/usr/bin/env python2.7
# coding: utf-8
"""
This script is used for project management.

See Fabric documentation for more info: http://docs.fabfile.org/en/1.10/index.html
"""

# Imports #####################################################################
from __future__ import print_function
import re
import time
from fabric.api import task
from fabric.colors import red
from pprint import pprint as pp
from pkg_resources import parse_version

# Internal
from .helpers import ex, true
from .ver import _get_version
from .constants import UPSTREAM_REPO

# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "11-JUL-2017"


TAGS = []


def _get_tags(cache=True, display='n'):
    """Returns the two latest tags."""
    global TAGS
    if cache and TAGS:

        if true(display):
            pp(TAGS[:2])

        return TAGS[:2]

    result = []
    raw_tags = ex('git log --date-order --tags --simplify-by-decoration --pretty=format:"%ai %h %d"')[0].split("\n")
    raw_tags = [x for x in raw_tags if "tag:" in x]

    for tag in raw_tags:
        match = re.search("(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?tag: (?P<tag>v.*?)[,\)]", tag)
        if match:
            result.append((
                match.group("tag"),
                parse_version(match.group("tag")),
                time.strptime(match.group("date"), "%Y-%m-%d %H:%M:%S")
            ))

    if cache:
        TAGS = result[:]

    if true(display):
        pp(TAGS[:2])

    return result[:2]


@task
def tags(cache=True, display='y'):
    """Returns the two latest tags."""
    return _get_tags(cache, display)


@task
def create_tag(push="yes"):
    """Creates a tag of the current version number"""
    ver = _get_version()
    print("Tag will be 'v{0}'".format(ver))
    val = raw_input("OK [Yn]? ")

    if true(val):
        ex('git tag -a v{0} -m "version {0}"'.format(ver))

        if push == "yes":
            # Push the new tag upstream and then re-sync
            ex("git push --follow-tags %s master" % UPSTREAM_REPO)

            print(("...updating local repo"))
            ex(["git", "fetch", "upstream"])
            ex(["git", "rebase", "upstream/master"])
            ex(["git", "push", "--follow-tags"])
        else:
            print(red("WARNING: Tag not pushed; use [git push --follow-tags %s master] to push it" % UPSTREAM_REPO))
    else:
        print(red("skipping tag"))


def push_origin():
    '''
    Push changes upstream and rebase the local fork.
    '''
    ex(["git", "push"])
