#!/usr/bin/env python

import os

from flask import Flask
from flask import render_template

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Load up our Search Blueprint and map the base URL to default to search.
    from . import search
    app.register_blueprint(search.bp)
    app.add_url_rule('/', view_func=search.query)

    return app
