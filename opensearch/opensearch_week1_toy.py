# This file is meant to capture the commands we submitted in the iPython REPL, therefore it is not "organized" and structured like a proper Python file.
import json

from opensearchpy import OpenSearch

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

# Do a few checks before we start indexing:
print(client.cat.health())
print(client.cat.indices())

# If you still have your documents from the Dev Tools test, we should be able to check them here:
print(client.cat.count("searchml_test", params={"v": "true"}))

# Create an index with non-default settings.
index_name = 'searchml_revisited'
index_body = {
    'settings': {
        'index': {
            'query': {
                'default_field': "body"
            }
        }
    }
}

response = client.indices.create(index_name, body=index_body)
print('\nCreating index:')
print(json.dumps(response, indent=4))

# Add our sample document to the index.
docs = [
    {
        "id": "doc_a",
        "title": "Fox and Hounds",
        "body": "The quick red fox jumped over the lazy brown dogs.",
        "price": "5.99",
        "in_stock": True,
        "category": "childrens"},
    {
        "id": "doc_b",
        "title": "Fox wins championship",
        "body": "Wearing all red, the Fox jumped out to a lead in the race over the Dog.",
        "price": "15.13",
        "in_stock": True,
        "category": "sports"},
    {
        "id": "doc_c",
        "title": "Lead Paint Removal",
        "body": "All lead must be removed from the brown and red paint.",
        "price": "150.21",
        "in_stock": False,
        "category": "instructional"},
    {
        "id": "doc_d",
        "title": "The Three Little Pigs Revisted",
        "price": "3.51",
        "in_stock": True,
        "body": "The big, bad wolf huffed and puffed and blew the house down. The end.",
        "category": "childrens"}
]

for doc in docs:
    doc_id = doc["id"]
    print("Indexing {}".format(doc_id))
    response = client.index(
        index=index_name,
        body=doc,
        id=doc_id,
        refresh=True
    )
    print('\n\tResponse:')
    print(json.dumps(response, indent=4))

# Verify they are in:
print(client.cat.count(index_name, params={"v": "true"}))

# Get the index mappings

print(client.indices.get_mapping(index_name))

# Create a new index, this time with different mappings
index_name = 'searchml_revisited_custom_mappings'
index_body = {
    'settings': {
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
            "in_stock": {"type": "boolean"},
            "category": {"type": "keyword", "ignore_above": "256"},
            "price": {"type": "float"}
        }
    }
}

response = client.indices.create(index_name, body=index_body)
print('\nCreating index:')
print(json.dumps(response, indent=4))

for doc in docs:
    doc_id = doc["id"]
    print("Indexing {}".format(doc_id))
    response = client.index(
        index=index_name,
        body=doc,
        id=doc_id,
        refresh=True
    )
    print('\n\tResponse:')
    print(response)

# Do some searches
q = 'dogs'
query = {
    'size': 5,
    'query': {
        'multi_match': {
            'query': q,
            'fields': ['title^2', 'body']
        }
    }
}

client.search(
    body=query,
    index=index_name
)

# try a phrase query
q = 'fox dog'
query = {
    'size': 5,
    'query': {
        'match_phrase': {
            'body': {"query": q}
        }
    }
}

client.search(
    body=query,
    index=index_name
)

# try a phrase query with slop
q = 'fox dog'
query = {
    'size': 5,
    'query': {
        'match_phrase': {
            'body': {"query": q, "slop": 10}
        }
    }
}

client.search(
    body=query,
    index=index_name
)

# try a match all query with a filter and a price factor
query = {
    'size': 5,
    'query': {
        "function_score": {
            "query": {
                "bool": {
                    "must": [
                        {"match_all": {}}
                    ],
                    "filter": [
                        {"term": {"category": "childrens"}}
                    ]
                }
            },
            "field_value_factor": {
                "field": "price",
                "missing": 1
            }
        }
    }
}

client.search(
    body=query,
    index=index_name
)

###################
# Aggregations

query = {
    'size': 0,
    'query': {
        "match_all": {}
    },
    'aggs': {
        "category": {
            "terms": {
                "field": "category",
                "size": 10,
                "missing": "N/A",
                "min_doc_count": 0
            }
        }
    }
}

client.search(
    body=query,
    index=index_name
)

# Terms on price
query = {
    'size': 0,
    'query': {
        "match_all": {}
    },
    'aggs': {
        "price": {
            "terms": {
                "field": "price",
                "size": 10,
                "min_doc_count": 0
            }
        }
    }
}

client.search(
    body=query,
    index=index_name
)

# Range aggregation
query = {
    'size': 0,
    'query': {
        "match_all": {}
    },
    'aggs': {
        "price": {
            "range": {
                "field": "price",
                "ranges": [
                    {
                        "to": 5
                    },
                    {
                        "from": 5,
                        "to": 20
                    },
                    {
                        "from": 20,
                    }
                ]
            }
        }
    }
}

client.search(
body = query,
index = index_name
)

######################################
#####
#####  DANGER!!!!!!!!!!!
#####
######################################
# if you want to delete the documents, but keep the index, run the following:
for doc in docs:
    doc_id = doc["id"]
print("Indexing {}".format(doc_id))
response = client.delete(
index = index_name,
id = doc_id,
)
print('\n\tResponse:')
print(response)

# If at any time you want to start over, run this command to delete the index and then you can start from the toop
# Delete the index.
response = client.indices.delete(
index = index_name
)

print('\nDeleting index:')
print(response)
