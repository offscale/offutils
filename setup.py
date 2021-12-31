from sys import version

from setuptools import find_packages, setup

if version[0] == "2":
    from itertools import imap as map, ifilter as filter

from ast import parse
from os import path

if __name__ == "__main__":
    package_name = "offutils"

    with open(path.join(package_name, "__init__.py")) as f:
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
        description="Shared library (for `off-` prefixed packages).",
        classifiers=[
            "Development Status :: 7 - Inactive",
            "Intended Audience :: Developers",
            "Topic :: Software Development",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "License :: OSI Approved :: MIT License",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
        ],
        install_requires=["pyyaml"],
        test_suite=package_name + ".tests",
        packages=find_packages(),
        package_dir={package_name: package_name},
    )
