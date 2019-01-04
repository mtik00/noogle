#!/usr/bin/env python
"""obfuscator package setup script."""
from __future__ import print_function
import os
from setuptools import setup, find_packages


THIS_DIR = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    setup(
        name="gcal_nest",
        version="0.0.0",
        description="Google Calendar <--> Nest controller",
        author="Timothy McFadden",
        author_email="tim@timandjamie.com",
        url="https://github.com/mtik00/gcal_nest",
        download_url=(
            "https://github.com/mtik00/gcal_nest/releases/download/v0.0.0/"
            "gcal_nest-0.0.0.tar.gz"
        ),
        install_requires=[
            "google-api-python-client",
            "setuptools",
            "arrow",
            "click",
            "sqlalchemy-utils",
            "sqlalchemy",
        ],
        extras_require={"dev": ["ruamel.yaml"]},
        packages=find_packages(exclude=("fabfile",)),
        zip_safe=True,
        include_package_data=True,
        test_suite="tests",
        license="MIT",
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Intended Audience :: Developers",
            "Environment :: Console",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Topic :: Home Automation",
            "Topic :: Internet",
        ],
        long_description=open(os.path.join(THIS_DIR, "README.md")).read(),
        entry_points={"console_scripts": ["gcal-nest=gcal_nest.cli:cli"]},
    )
