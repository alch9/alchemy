#!/bin/bash

export FLASK_ENV=development

FLASK_APP=webapp.alchemyapp flask run $*
