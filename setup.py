from setuptools import setup
from ast import parse

if __name__ == "__main__":
    package_name = "offutils"

    with open(package_name + ".py") as f:
        __author__, __version__ = list(
            map(
                lambda buf: next([e.value.s for e in parse(buf).body]),
                list(
                    filter(
                        lambda line: line.startswith("__version__")
                        or line.startswith("__author__"),
                        f,
                    )
                ),
            )
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
