#
# A simple endpoint that can receive documents from an external source, mark them up and return them.  This can be useful
# for hooking in callback functions during indexing to do smarter things like classification
#
from flask import (
    Blueprint, request, abort, current_app, jsonify
)
import fasttext
import json

bp = Blueprint('documents', __name__, url_prefix='/documents')

def get_synonyms(name):
    response = []
    syns_model = current_app.config.get("syns_model", None) # see if we have a synonyms/analogies model

    for token in name.lower().split(' '):
        predictions = syns_model.get_nearest_neighbors(token)
        for item in predictions:
            if item[0] > 0.85:
                response.append(item[1])
    
    return {"name_synonyms": response}

@bp.route('/annotate_test', methods=['GET'])
def annotate_get():
    args = request.args

    return jsonify(get_synonyms(args.get("name")))


# Take in a JSON document and return a JSON document
@bp.route('/annotate', methods=['POST', 'GET'])
def annotate():
    if request.mimetype == 'application/json':
        the_doc = request.get_json()
        print(the_doc)
        response = {}
        cat_model = current_app.config.get("cat_model", None) # see if we have a category model
        syns_model = current_app.config.get("syns_model", None) # see if we have a synonyms/analogies model
        # We have a map of fields to annotate.  Do POS, NER on each of them
        sku = the_doc["sku"]
        for item in the_doc:
            the_text = the_doc[item]
            if the_text is not None and the_text.find("%{") == -1:
                if item == "name":
                    if syns_model is not None:
                        predictions = syns_model.get_nearest_neighbors(the_text.lower())
                        response = []

                        for item in predictions:
                            if item[0] > 0.85:
                                response.append(item[1])
                        
        return jsonify({"name_synonyms": " ".join(response)})
    abort(415)
