#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pip setup file
"""
import os
import sys
import codecs
from setuptools import setup


CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(CURRENT_DIRECTORY, "README.rst"), encoding="utf-8") as f:
    LONG_DESCRIPTION = "\n" + f.read()


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

REQUIRED = ["boto3"]

setup(
    name="bucketstore",
    version="0.2.0",
    description="A simple library for interacting with Amazon S3.",
    long_description=LONG_DESCRIPTION,
    author="Kenneth Reitz, Jacobi Petrucciani",
    author_email="jacobi@mimirhq.com",
    url="https://github.com/jpetrucciani/bucketstore",
    py_modules=["bucketstore"],
    install_requires=REQUIRED,
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
