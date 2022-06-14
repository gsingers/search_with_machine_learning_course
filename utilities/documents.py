# A set of methods for annotating a document before it gets indexed
# Implement the week 2 annotation assignment
import fasttext


def annotate(doc: dict, syns_model: dict):
    #### Level 3 Integrate Synonyms
    for item in doc:
        the_text = doc[item]
        if the_text is not None and item == "name" and syns_model is not None:
            # Implement to add synonyms for the name field.
            synonyms = None
            if synonyms is not None:
                doc["name_synonyms"] = synonyms