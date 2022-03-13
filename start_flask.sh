#!/usr/bin/env bash
echo "Running ${0}"
export FLASK_ENV=development
export FLASK_APP=week4/__init__.py
export PRIOR_CLICKS_LOC=workspace/ltr_output/train.csv

flask run