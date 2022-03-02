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
            if the_text is not None and "%{" not in the_text:
                if item == "name":
                    # print("the_text", the_text)
                    if syns_model is not None:
                        how_many_neighbors = 20
                        neighbors = syns_model.get_nearest_neighbors(the_text, k=how_many_neighbors)

                        threshold = 0.90
                        synonyms = [n[1] for n in neighbors if n[0] >= threshold]

                        # print("Neighbors of '%s': %s" % (the_text, neighbors))
                        # print("Synonyms of '%s': %s" % (the_text, synonyms))
                        response["name_synonyms"] = synonyms
        return jsonify(response)
    abort(415)
