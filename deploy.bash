#!/usr/bin/env bash
# NOTE: This should be run in an already-activate virtual environment on the
# target host.

# Make sure we bring in any changes to python #################################
pip install -e .
###############################################################################

# make sure the build directory is clear
if [[ ! -d "_build" ]]; then
    mkdir _build
else
    rm -rf _build/*
fi

# build the config files
# flask build

# Upgrade the database
# flask db upgrade

# bootstrap the built deploy file
# sudo bash _build/deploy.bash