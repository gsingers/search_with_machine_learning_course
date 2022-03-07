#
# A simple endpoint that can receive documents from an external source, mark them up and return them.  This can be useful
# for hooking in callback functions during indexing to do smarter things like classification
#
from flask import (
    Blueprint, request, abort, current_app, jsonify
)
import fasttext
import json
import string
import nltk
from nltk.stem.snowball import EnglishStemmer

english_stemmer = EnglishStemmer()


def transform_value(value: str, model) -> str:
    translation_table = str.maketrans("", "", string.punctuation)
    words = value.translate(translation_table)
    # words = [stemmer.stem(w.strip()) for w in value]
    synonyms = set()
    tokens = nltk.word_tokenize(words)
    stemmed_tokens = [english_stemmer.stem(token) for token in tokens]

    for token in stemmed_tokens:
        output = model.get_nearest_neighbors(token)
        for synonym in output:
            if synonym[0] >= 0.9:
                synonyms.add(synonym[1])

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
                        response['name_synonyms'] = transform_value(the_text, syns_model)
        return jsonify(response)
    abort(415)