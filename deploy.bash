#!/usr/bin/env bash
# NOTE: This should be run in an already-activated virtual environment on the
# target host.

# Make sure we bring in any changes to python #################################
pip install -e .[dev]
###############################################################################

# build the config files
gcal-nest dev build

# TODO: Upgrade the database?

# bootstrap the built deploy file
# sudo bash _build/deploy.bash
