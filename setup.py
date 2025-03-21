#!/usr/bin/env python

"""The setup script."""

from sys import version
from setuptools import find_packages, setup


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "httpx>=0.24.1",
    "pyjwt>=2.4.0",
    "attrs>=23.2.0",
    "mmh3>=3.0.0",
    "requests>=2.31.0",
    "tenacity>=8.2.0",
    "typing_extensions>=4.7.1"
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Harness",
    author_email="support@harness.io",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Feature flag server SDK for python",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords="featureflags",
    name="harness-featureflags",
    packages=find_packages(include=["featureflags", "featureflags.*", "featureflags.openapi", "featureflags.openapi.config",  "featureflags.openapi.metrics"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/harness/ff-python-server-sdk",
    version='1.7.2',
    zip_safe=False,
)
