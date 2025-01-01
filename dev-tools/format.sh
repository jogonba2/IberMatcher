#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place "ibermatcher" --exclude=__init__.py
isort "ibermatcher"
black "ibermatcher" -l 80