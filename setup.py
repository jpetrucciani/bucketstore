#!/usr/bin/env python
"""
pip setup file
"""
from setuptools import setup


__library__ = "bucketstore"
__version__ = "VERSION"

__user__ = "https://github.com/jpetrucciani"


with open("README.md", encoding="UTF-8") as readme:
    LONG_DESCRIPTION = readme.read()


REQUIRED = ["boto3"]

setup(
    name=__library__,
    version=__version__,
    description="A simple library for interacting with Amazon S3.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Kenneth Reitz, Jacobi Petrucciani",
    author_email="j@cobi.dev",
    url=f"{__user__}/{__library__}.git",
    download_url=f"{__user__}/{__library__}.git",
    py_modules=[__library__],
    install_requires=REQUIRED,
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
