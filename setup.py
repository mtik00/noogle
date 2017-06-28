#!/usr/bin/env python
'''obfuscator package setup script.'''
from __future__ import print_function
import os
from setuptools import setup, find_packages


THIS_DIR = os.path.abspath(os.path.dirname(__file__))


if __name__ == '__main__':
    setup(
        name="gcal_nest",
        version="1.0.0",
        description="Google Calendar <--> Nest controller",
        author="Timothy McFadden",
        url="https://github.com/mtik00/gcal_nest",
        download_url=(
            "https://github.com/mtik00/gcal_nest/releases/download/v{0}/"
            "gcal_nest-{0}.tar.gz").format("1.0.0"),
        install_requires=[
            "python-nest>=3.0",
            "google-api-python-client",
            "setuptools",
            "arrow",
            "click",
        ],
        packages=find_packages(exclude=('fabfile',)),
        zip_safe=True,
        include_package_data=True,
        test_suite="tests",
        license='MIT',

        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Intended Audience :: Developers',
            'Environment :: Console',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Topic :: Home Automation',
            'Topic :: Internet'
        ],

        long_description=open(os.path.join(THIS_DIR, "README.md")).read(),

        entry_points={
            'console_scripts': ['gcal_nest=gcal_nest.cli:cli'],
        }
    )
