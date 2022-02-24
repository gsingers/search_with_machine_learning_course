import os

from flask import Flask
from flask import render_template
import pandas as pd
import fasttext
from pathlib import Path

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
        else:
            print("No prior clicks to load.  This may effect quality. Run ltr-end-to-end.sh per week 2 if you want")
        #print(app.config)
        SYNS_MODEL_LOC = os.environ.get("SYNONYMS_MODEL_LOC", "/workspace/datasets/fasttext/syns_model.bin")
        print("SYNS_MODEL_LOC: %s" % SYNS_MODEL_LOC)
        if SYNS_MODEL_LOC and os.path.isfile(SYNS_MODEL_LOC):
            app.config["syns_model"] = fasttext.load_model(SYNS_MODEL_LOC)
        else:
            print("No synonym model found.  Have you run fasttext?")
        app.config["index_name"] = os.environ.get("INDEX_NAME", "bbuy_annotations")
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
    from . import documents
    app.register_blueprint(documents.bp)
    app.add_url_rule('/', view_func=search.query)

    return app
