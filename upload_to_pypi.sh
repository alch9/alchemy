#!/bin/bash

# Install from test URL
# pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple alchemy

if [ "$1" = "prod" ]; then
    echo "Export to prod not allowed right now"
    exit 1
else
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
fi
