#
# A simple endpoint that can receive documents from an external source, mark them up and return them.  This can be useful
# for hooking in callback functions during indexing to do smarter things like classification
#
from typing import List

from flask import (
    Blueprint, request, abort, current_app, jsonify
)

import fasttext
import re
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer('english')
model = fasttext.load_model('week3/phone_model.bin')


def transform_value(value: str) -> str:
    value = value.replace('\n', ' ')
    value = re.sub("[^0-9a-zA-Z]+", " ", value).lower()

    words = value.split()
    #words = [stemmer.stem(w.strip()) for w in value]

    synonyms = set()
    for word in words:
        for s in model.get_nearest_neighbors(word):
            if s[0] > 0.9:
                synonyms.add(s[1])
    return " ".join(synonyms)


bp = Blueprint('documents', __name__, url_prefix='/documents')


# Take in a JSON document and return a JSON document
@bp.route('/annotate', methods=['POST'])
def annotate():
    if request.mimetype == 'application/json':
        the_doc = request.get_json()
        response = {}
        cat_model = current_app.config.get("cat_model", None)  # see if we have a category model
        syns_model = current_app.config.get("syns_model", None)  # see if we have a synonyms/analogies model
        # We have a map of fields to annotate.  Do POS, NER on each of them
        sku = the_doc["sku"]
        for item in the_doc:
            the_text = the_doc[item]
            if the_text is not None and the_text.find("%{") == -1:
                if item == "name":
                    if syns_model is not None:
                        response[f'{item}_synonyms'] = transform_value(the_text)
        return jsonify(response)
    abort(415)
