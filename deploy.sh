#! /bin/bash
#
# deploy.sh
# Copyright (C) 2015 dhilipsiva <dhilipsiva@gmail.com>
#
# Distributed under terms of the MIT license.
#


python setup.py sdist
python setup.py bdist_wheel
python setup.py sdist upload
python setup.py bdist_wheel upload
