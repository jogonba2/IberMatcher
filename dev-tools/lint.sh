#!/usr/bin/env bash

set -e
set -x

mypy "ibermatcher"
flake8 "ibermatcher" --ignore=E501,W503,E203,E402,E704
black "ibermatcher" --check -l 80
