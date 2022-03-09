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

def load_synonyms(text,syns_model):
    synonyms=[]
    tokens = nltk.word_tokenize(text)
    for token in tokens:
        output=syns_model.get_nearest_neighbors(token)
        for synonym in output:
                if synonym[0]>=0.9:
                    synonyms.append(synonym[1])
    return synonyms

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
            the_text = the_doc[item]
            if the_text is not None and the_text.find("%{") == -1:
                if item == "name":
                    if syns_model is not None:
                        response['name_synonyms'] = load_synonyms(the_text,syns_model)
        return jsonify(response)
    abort(415)
