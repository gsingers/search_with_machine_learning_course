# This file is meant to capture the commands we submitted in the iPython REPL, therefore it is not "organized" and structured like a proper Python file.

#######################
#
# Setup work.  See below for main content.
#
#######################


import json

import nltk
from opensearchpy import OpenSearch

# Do some setup work
nltk.download('words')
nltk.download('maxent_ne_chunker')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('popular')

host = 'localhost'
port = 9200
auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

# Create the client with SSL/TLS enabled, but hostname and certificate verification disabled.
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    # client_cert = client_cert_path,
    # client_key = client_key_path,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

# Create an index with non-default settings.
# Create a new index, this time with different mappings
index_name = 'searchml_week3'
index_body = {
    'settings': {
        "analysis": {
            "filter": {
                "pos_filter": {
                    "type": "pattern_capture",
                    "preserve_original": True,
                    "patterns": ["(.*)#(.*)"]
                }
            },
            "analyzer": {

                "body_pos": {
                    "tokenizer": "whitespace",  # we can't use standard b/c it strips or delimiters
                    "filter": ["pos_filter", "lowercase"]  # put whatever else here
                },
                "body_pos_search": {
                    "tokenizer": "whitespace",  # we can't use standard b/c it strips or delimiters
                    "filter": ["lowercase"]  # put whatever else here
                }

            }
        },
        'index': {
            'query': {
                'default_field': "body"
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "english"},
            "body": {"type": "text", "analyzer": "english"},
            "body_sentences": {"type": "text", "analyzer": "english"},
            # Notice the different search analyzer
            "body_pos": {"type": "text", "analyzer": "body_pos", "search_analyzer": "body_pos_search"},

            "body_ne": {"type": "text", "analyzer": "standard"},
            "in_stock": {"type": "boolean"},
            "category": {"type": "keyword", "ignore_above": "256"},
            "price": {"type": "float"}
        }
    }
}

try:
    client.indices.delete(index_name)
except:
    pass
client.indices.create(index_name, body=index_body)

# Add our sample document to the index.
docs = [
    {
        "id": "doc_b",
        "title": "Wayne Gretzky",
        "body": "The greatest hockey player of all time is Wayne Gretzky. He holds a record for holding the most records!  Who else even comes close?",
        "price": "15.13",
        "in_stock": True,
        "category": "sports"},
    {
        "id": "doc_a",
        "title": "Apple iPhone 13",
        "body": "The all new Apple iPhone 13 has 3 cameras and the fastest chip on the market.  The phone retails for $699 for 64GB of storage.",
        "price": "5.99",
        "in_stock": True,
        "category": "childrens"},

    {
        "id": "doc_c",
        "title": "Lead Paint Removal",
        "body": "All lead must be removed from the brown and red paint.  Use the Glidden Lead Paint Killer solvent to keep the paint, but remove the lead!",
        "price": "150.21",
        "in_stock": False,
        "category": "instructional"},
    {
        "id": "doc_d",
        "title": "The Three Little Pigs Revisted",
        "price": "3.51",
        "in_stock": True,
        "body": "The big, bad wolf huffed and puffed and blew the house down. The end.  Well, not quite.  It seems the pigs filed an injunction against the wolf and now the wolf has to pay restitution.",
        "category": "childrens"},
    {
        "id": "doc_e",
        "title": "Green apples and Spam",
        "price": "2.99",
        "in_stock": True,
        "body": "The little green apple fell from the tree.  It was not a bad apple, so no one could understand why it fell.",
        "category": "childrens"},
    {
        "id": "doc_f",
        "title": "Fun with Spans",
        "price": "4.99",
        "in_stock": True,
        "body": "Dan is the President. The United States Government has arrested him.",
        "category": "childrens"}

]

#######################
#
# Start Here: Main Class Content
#
#######################



def get_entities(named_entities, entity_types):
    result = ""
    for ent in named_entities:  # two cases: we have a NNP or we have a tree
        if isinstance(ent, tuple):
            e_type = ent[1]
            if e_type in entity_types:
                result += ent[0] + " "
        elif isinstance(ent, nltk.Tree):
            if ent.label() in entity_types:
                # these are tuples, we want all of them, but just the first part
                result += "_".join([x[0] for x in ent.leaves()])

    return result


for doc in docs:
    doc_id = doc["id"]
    for item in ["body"]:  # Just do body for now
        value = doc[item]
        tokens = nltk.word_tokenize(value)
        sentences = nltk.sent_tokenize(value)
        pos = nltk.pos_tag(tokens)
        named_entities = nltk.ne_chunk(pos)
        doc["%s_sentences" % item] = " ".join("__SB__ %s __SE__" % x for x in sentences)
        doc["%s_pos" % item] = " ".join(["#".join([x[0], "__%s__" % x[1]]) for x in pos])
        doc["%s_ne" % item] = get_entities(named_entities, {"ORGANIZATION", "PERSON", "NNP"})
    print("Indexing {} as: {}".format(doc_id, json.dumps(doc, indent=4)))

    client.index(
        index=index_name,
        body=doc,
        id=doc_id,
        refresh=True
    )

# Verify they are in:
print(client.cat.count(index_name, params={"v": "true"}))
print("Proper Noun Apple")
# Do fine Apple as a proper noun
q = 'apple#__NNP__'
query = {
    'size': 5,
    'query': {
        'query_string': {
            'query': q,
            'fields': ['body_pos']
        }
    }
}

rsp = client.search(
    body=query,
    index=index_name
)

print(json.dumps(rsp, indent=2))
print("Plain ol Apple")
# Do fine Apple as a common noun
q = 'apple#__NN__'
query = {
    'size': 5,
    'query': {
        'query_string': {
            'query': q,
            'fields': ['body_pos']
        }
    }
}

rsp = client.search(
    body=query,
    index=index_name
)

print(json.dumps(rsp, indent=2))

# Sentence query.  going to use a new type of query called a SpanQuery
q = 'President United States'  # should return one match
query = {
    'size': 5,
    'query': {
        'query_string': {
            'query': q,
            'fields': ['body_pos']
        }
    }
}

rsp = client.search(
    body=query,
    index=index_name
)

print(json.dumps(rsp, indent=2))


# Should return no match
query = {
    'size': 5,
    'query': {
        "span_within":{
            "little":{
                "span_near": {
                    "clauses":[
                        {"span_term": {"body_sentences": "President"}},
                        {"span_term": {"body_sentences": "United"}},
                        {"span_term": {"body_sentences": "States"}}
                    ]
                }
            },
            "big":{
                "span_near": {
                    "clauses":[
                        {"span_term": {"body_sentences": "__SB__"}},
                        {"span_term": {"body_sentences": "__SE__"}},
                    ]
                }
            }
        }
    }
}

rsp = client.search(
    body=query,
    index=index_name
)

print(json.dumps(rsp, indent=2))