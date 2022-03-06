#
# A simple endpoint that can receive documents from an external source, mark them up and return them.  This can be useful
# for hooking in callback functions during indexing to do smarter things like classification
#
from flask import (
    Blueprint, request, abort, current_app, jsonify
)
import fasttext
import json
import nltk
import re

nltk.download('punkt')
nltk.download('stopwords')

bp = Blueprint('documents', __name__, url_prefix='/documents')

THRESHOLD = 0.91

def extract_synonyms(name_text, syns_model):
    syns = set()
    tokens = nltk.word_tokenize(name_text)
    for token in tokens:
        # Do not stem here, as stemmed tokens would fetch various words
        cleaned_token = re.sub(r'[^a-zA-Z0-9]', '', token.strip().lower())
        syns.update([syn for score, syn in syns_model.get_nearest_neighbors(cleaned_token) if score > THRESHOLD])
    final_syns = list(syns)
    return final_syns

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
                        response["name_synonyms"] = extract_synonyms(the_text, syns_model)
        return jsonify(response)
    abort(415)
