from setuptools import setup
from sys import version
from ast import parse

if version[0] == '2':
    from itertools import imap as map, ifilter as filter


if __name__ == "__main__":
    package_name = "offutils"

    with open(package_name + ".py") as f:
        __author__, __version__ = map(
            lambda buf: next(map(lambda e: e.value.s, parse(buf).body)),
            filter(
                lambda line: line.startswith("__version__")
                or line.startswith("__author__"),
                f,
            ),
        )

    setup(
        name=package_name,
        author=__author__,
        version=__version__,
        description="Utility functions for many off- prefixed python modules",
        classifiers=[
            "Development Status :: 7 - Inactive",
            "Intended Audience :: Developers",
            "Topic :: Software Development",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "License :: OSI Approved :: MIT License",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
        ],
        test_suite="tests",
        py_modules=[package_name],
    )
