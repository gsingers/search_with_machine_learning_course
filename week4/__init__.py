import os
import fasttext

from flask import Flask
from flask import render_template

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    model_path = "/workspace/search_with_machine_learning_course/week4/model.bin"
    app.config["query_model"] = fasttext.load_model(model_path)
    app.config["index_name"] = os.environ.get("INDEX_NAME", "bbuy_products")


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
