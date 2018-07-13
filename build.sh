#!/bin/bash

rm -fR alchemy.egg-info build dist

python setup.py sdist bdist_wheel
