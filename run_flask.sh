#!/bin/bash
export FLASK_ENV=development
export FLASK_APP=$1 

flask run --port 3000