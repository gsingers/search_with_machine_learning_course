#
# A simple endpoint that can receive documents from an external source, mark them up and return them.  This can be useful
# for hooking in callback functions during indexing to do smarter things like classification
#
import nltk
from flask import (
    Blueprint, request, abort, current_app, jsonify
)
import fasttext
import json

bp = Blueprint('documents', __name__, url_prefix='/documents')

def get_entities(named_entities, entity_types=["ORGANIZATION", "PERSON", "NNP"]):
    result = ""
    for ent in named_entities:  # two cases: we have a NNP or we have a tree
        print("IMPLEMENT_ME: get_entities")

    return result

# Take in a JSON document and return a JSON document
@bp.route('/annotate', methods=['POST'])
def annotate():
    if request.mimetype == 'application/json':
        the_doc = request.get_json()
        response = {}
        cat_model = current_app.config.get("cat_model", None) # see if we have a category model
        syns_model = current_app.config.get("syns_model", None) # see if we have a synonyms/analogies model
        # We have a map of fields to annotate.  Do POS, NER on each of them
        sku = the_doc["sku"]
        for item in the_doc:
            if item != "sku":
                the_text = the_doc[item]
                print("IMPLEMENT ME: annotate()")

        print(json.dumps(response, indent=2))

        return jsonify(response)
    abort(415)
