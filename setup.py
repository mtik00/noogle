#!/usr/bin/env python
"""obfuscator package setup script."""
import os
from setuptools import setup, find_packages


THIS_DIR = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    setup(
        name="noogle",
        version="0.0.0",
        description="Google Calendar <--> Nest controller",
        author="Timothy McFadden",
        author_email="tim@timandjamie.com",
        url="https://github.com/mtik00/noogle",
        download_url=(
            "https://github.com/mtik00/noogle/releases/download/v0.0.0/"
            "noogle-0.0.0.tar.gz"
        ),
        install_requires=[
            "google-api-python-client",
            "setuptools",
            "arrow",
            "click",
            "sqlalchemy-utils",
            "sqlalchemy",
            "oauth2client",
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
        entry_points={"console_scripts": ["noogle=noogle.cli:cli"]},
    )
