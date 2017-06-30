#!/bin/bash

set -xeuo pipefail

rm -rf dist/
python setup.py sdist
twine upload dist/*
