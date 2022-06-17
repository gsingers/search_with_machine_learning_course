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
        if the_doc is not None and the_doc != "":

            response = {}
            # We have a map of fields to annotate.  Do POS, NER on each of them
            val = the_doc["name"]
            if val is not None and len(val) > 0:
                the_text = val[0]
                print(the_text)
                if the_text is not None:
                    # Implement to add synonyms for the name field.
                    result = []
                    syns_model = current_app.config.get("syns_model", None) # see if we have a synonyms/analogies model
                    #### Level 3 Derive Synonyms
                    print("IMPLEMENT ME: call nearest_neighbors on your syn model and return it as `name_synonyms`")
                    response["name_synonyms"] = result
                else:
                    print(f"Unable to process {the_doc}")
            else:
                print(f"Unable to process {the_doc}")
            return jsonify(response)
        else:
            print("Unable to process request.  Doc is empty or None")
    abort(415)
