import os

from flask import Flask
from flask import render_template
import pandas as pd

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_envvar('LTR_APPLICATION_SETTINGS', silent=True)
        PRIOR_CLICKS_LOC = os.environ.get("PRIOR_CLICKS_LOC", "/workspace/ltr_output/train.csv")
        print("PRIOR CLICKS: %s" % PRIOR_CLICKS_LOC)
        if PRIOR_CLICKS_LOC and os.path.isfile(PRIOR_CLICKS_LOC):
            priors = pd.read_csv(PRIOR_CLICKS_LOC)
            priors_gb = priors.groupby("query")
            app.config["priors_df"] = priors
            app.config["priors_gb"] = priors_gb
        #print(app.config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # A simple landing page
    #@app.route('/')
    #def index():
    #    return render_template('index.jinja2')

    from . import search
    app.register_blueprint(search.bp)
    app.add_url_rule('/', view_func=search.query)

    return app
