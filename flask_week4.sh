#!/usr/bin/env bash
set -x 

export QUERY_CLASS_MODEL_LOC=/workspace/datasets/week4/model.mq100.e5.lr0.5.ng2.bin
export FLASK_APP=week4
export FLASK_ENV=development

flask run
