import json
import sys
import tempfile
from urllib.parse import urljoin

import requests
import xgboost as xgb
from opensearchpy import OpenSearch
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from xgboost import plot_tree

#######################
#
# Setup work
#
#######################
host = 'localhost'
port = 9200
base_url = "https://{}:{}/".format(host, port)
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
        "title": "The Three Little Pigs Revisited",
        "price": "3.51",
        "in_stock": True,
        "body": "The big, bad wolf huffed and puffed and blew the house down. The end.",
        "category": "childrens"},
    {
        "id": "doc_e",
        "title": "Pigs in a Blanket and Other Recipes",
        "price": "27.50",
        "in_stock": True,
        "body": "Pigs in a blanket aren't as cute as you would think given it's a food and not actual pigs wrapped in blankets.",
        "category": "instructional"},
    {
        "id": "doc_f",
        "title": "Dogs are the best",
        "body": "Dogs beat cats every day of the week and twice on Sunday. A dog is always up for doing something.  Since there are so many dog breeds, there is a dog for everyone!",
        "price": "50.99",
        "in_stock": True,
        "category": "childrens"},
    {
        "id": "doc_g",
        "title": "Dog",
        "body": "Dogs rule",
        "price": "5.99",
        "in_stock": True,
        "category": "childrens"},
    {
        "id": "doc_h",
        "title": "Dog: The bounty hunter: living in the red",
        "body": "Dog is a bounty hunter who goes on pretend missions with his friends, one of whom is the Fox",
        "price": "125.99",
        "in_stock": True,
        "category": "sports"},
]

# Create a new index
index_name = 'searchml_ltr'
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

client.indices.delete(index_name, ignore_unavailable=True)
client.indices.create(index_name, body=index_body)
# Index our documents
print("Indexing our documents")
for doc in docs:
    doc_id = doc["id"]
    print("\tIndexing {}".format(doc_id))
    client.index(
        index=index_name,
        body=doc,
        id=doc_id,
        refresh=True
    )

# Verify they are in:
print("We indexed:\n{}".format(client.cat.count(index_name, params={"v": "true"})))

#######################
#
# Step 1: Setup LTR storage
#
#######################

# Turn on the LTR store and name it the same as our index
ltr_store_name = index_name
ltr_store_path = "_ltr/" + ltr_store_name

print("Create our LTR store")
# LTR requests are not supported by the OpenSearchPy client, so we will drop down to using Python's Requests library
ltr_model_path = urljoin(base_url, ltr_store_path)
# Delete any old storage
resp = requests.delete(ltr_model_path, auth=auth, verify=False)
print("\tDeleted old store response status: %s" % resp.status_code)
# Create our new LTR storage
resp = requests.put(ltr_model_path, auth=auth, verify=False)
print("\tCreate the new store response status: %s" % resp.status_code)

#######################
#
# Step 2: Setup LTR Featureset
#
#######################
featureset_name = "ltr_toy"
headers = {"Content-Type": 'application/json'}
featureset_path = urljoin(ltr_model_path + "/", "_featureset/{}".format(featureset_name))
# Upload our feature set to our model
body_query_feature_name = "body_query"
title_query_feature_name = "title_query"
price_func_feature_name = "price_func"
print("\tUpload our features to the LTR storage")
ltr_feature_set = {"featureset": {
    "features": [
        {  # Instead of using our multifield query_string match, break it out into parts
            "name": title_query_feature_name,
            "params": ["keywords"],
            "template_language": "mustache",
            "template": {
                "match": {
                    "title": "{{keywords}}"
                }
            }
        },
        {  # Instead of using our multifield query_string match, break it out into parts
            "name": body_query_feature_name,
            "params": ["keywords"],
            "template_language": "mustache",
            "template": {
                "match": {
                    "body": "{{keywords}}"
                }
            }
        },
        # factor in price, albeit naively for this purpose, in practice we should normalize it, which we will do in the project!
        {
            "name": ("%s" % price_func_feature_name),
            "template_language": "mustache",
            "template": {
                "function_score": {
                    "functions": [{
                        "field_value_factor": {
                            "field": "price",
                            "missing": 0
                        }
                    }],
                    "query": {
                        "match_all": {}
                    }
                }
            }

        }
    ]
}}
resp = requests.post(featureset_path, headers=headers, data=json.dumps(ltr_feature_set), auth=auth, verify=False)

#######################
#
# Step 3: Collect Judgments
#
#######################
# Create a place to store our judgments
class Judgment:

    def __init__(self, query, doc_id, display_name, grade=0, features=[], query_str=None):
        self.query = query
        self.query_str = query_str
        self.doc_id = doc_id
        self.display_name = display_name
        self.grade = grade
        self.features = features

    # Modified from https://github.com/o19s/elasticsearch-ltr-demo/blob/master/train/judgments.py
    def toXGBFormat(self):
        featuresAsStrs = ["%s:%s" % (idx + 1, feature.get('value', 0)) for idx, feature in enumerate(self.features)]
        comment = "# %s\t%s" % (self.doc_id, self.query_str)
        return "%s\tqid:%s\t%s %s" % (self.grade, self.query, "\t".join(featuresAsStrs), comment)


# Create a map for tracking queries
queries = {1: "dogs", 2: "red fox", 3: "wolf huffed AND puffed OR pig"}
# A map where the key is the query id and the value is a list of judgments, one per document rated for that query
judgments = {}

# Loop over queries, execute a search
for query in queries:
    # Used to get the original queries to create the judgments
    query_obj = {
        'size': 5,
        'query': {
            'multi_match': {
                'query': queries[query],
                'fields': ['title^2', 'body']
            }
        }
    }
    print("################\nExecuting search: qid: {}; query: {}\n##########".format(query, queries[query]))
    response = client.search(body=query_obj, index=index_name)
    hits = response['hits']['hits']
    if len(hits) > 0:
        print(
            "For each hit answer the question: 'Is this hit relevant(1) or not relevant(0) to the query: {}?':".format(
                queries[query]))
        judge_vals = judgments.get(query)
        if judge_vals is None:
            judge_vals = []
            judgments[query] = judge_vals
        for hit in hits:
            print("Title: {}\n\nBody: {}\n".format(hit['_source']['title'], hit['_source']['body']))
            print("Enter 0 or 1:")
            input = ""
            for input in sys.stdin.readline():
                grade = input.rstrip()
                if grade == "0" or grade == "1":
                    judgment = Judgment(query, hit['_id'], hit['_source']['title'], int(grade))
                    judge_vals.append(judgment)
                    break
                elif grade == "skip" or grade == "s":
                    break
                elif grade == "exit" or grade == 'e':
                    input = grade  # set this back to the trimmed grade so we can exit the outer loop.  Very clunky!
                    break
            if input == "exit" or input == "e":
                break  # break out of hits, this is ugly, but OK for what we are doing here

#######################
#
# Step 4: Create Training Data (AKA Feature Logging)
#
#######################
# Coming out of this loop, we should have an array of judgments
train_file = tempfile.NamedTemporaryFile(delete=False)
# Log our features by sending our query and it's judged documents to OpenSearch
for (idx, item) in enumerate(judgments.items()):
    judge_vals = item[1]
    # create a new SLTR query with an appropriate filter query
    doc_ids = []
    for judgment in judge_vals:
        # Note: we are executing one query per judgment doc id here because it's easier, but we could do this
        # by adding all the doc ids for this query and scoring them all at once and cut our number of queries down
        # significantly
        # Create our SLTR query, filtering so we only retrieve the doc id in question
        query_obj = {
            'query': {
                'bool': {
                    "filter": [  # use a filter so that we don't actually score anything
                        {
                            "terms": {
                                "_id": [judgment.doc_id]
                            }
                        },
                        {  # use the LTR query bring in the LTR feature set
                            "sltr": {
                                "_name": "logged_featureset",
                                "featureset": featureset_name,
                                "store": ltr_store_name,
                                "params": {
                                    "keywords": queries[judgment.query]
                                }
                            }
                        }
                    ]
                }
            },
            # Turn on feature logging so that we get weights back for our features
            "ext": {
                "ltr_log": {
                    "log_specs": {
                        "name": "log_entry",
                        "named_query": "logged_featureset"
                    }
                }
            }
        }
        # Run the query just like any other search
        response = client.search(body=query_obj, index=index_name)
        print(response)
        # For each response, extract out the features and build our training features
        # We are going to do this by iterating through the hits, which should be in doc_ids order and put the
        # values back onto the Judgment object, which has a place to store these.
        if response and len(response['hits']) > 0 and len(response['hits']['hits']) == 1:
            hits = response['hits']['hits']
            # there should only be one hit
            judgment.features = hits[0]['fields']['_ltrlog'][0]['log_entry']
            # 		<grade> qid:<query_id> <feature_number>:<weight>... # <doc_id> <comments>
            # see https://xgboost.readthedocs.io/en/latest/tutorials/input_format.html
            xgb_format = judgment.toXGBFormat() + "\n"
            print(xgb_format)
            train_file.write(bytes(xgb_format, 'utf-8'))
        else:
            print("Weirdness. Fix")

train_file.close()

#######################
#
# Step 5: Train and Test with XGBoost
#
#######################
# Modified from https://github.com/o19s/elasticsearch-learning-to-rank/blob/main/demo/xgboost-demo/xgb.py
# Read the LibSVM labels/features

# We need to tell XGB what are features are called so that we can properly write out a model after training
feat_map_file = tempfile.NamedTemporaryFile(delete=False)
feat_map_file.write(bytes("0\tna\tq\n", "utf-8"))
feat_map_file.write(bytes('1\t{}\tq\n'.format(title_query_feature_name), 'utf-8'))
feat_map_file.write(bytes('2\t{}\tq\n'.format(body_query_feature_name), 'utf-8'))
feat_map_file.write(bytes('3\t{}\tq\n'.format(price_func_feature_name), 'utf-8'))
feat_map_file.close()
dtrain = xgb.DMatrix(train_file.name)
param = {'max_depth': 5,  'silent': 1, 'objective': 'reg:linear'}
num_round = 5
print("Training XG Boost")
bst = xgb.train(param, dtrain,
                num_round)  # Do the training.  NOTE: in this toy example we did not use any hold out data
model = bst.get_dump(fmap=feat_map_file.name, dump_format='json')

# We need to escape entries for uploading to OpenSearch, per the docs
model_str = '[' + ','.join(list(model)) + ']'

# Create our metadata for uploading the model
model_name = "ltr_toy_model"

os_model = {
    "model": {
        "name": model_name,
        "model": {
            "type": "model/xgboost+json",
            "definition": '{"objective":"reg:linear", "splits":' + model_str + '}'
        }
    }
}
#######################
#
# Step 6: Deploy your Model
#
#######################
# Upload the model to OpenSearch
model_path = urljoin(featureset_path + "/", "_createmodel")
print("Uploading our model to %s" % model_path)
response = requests.post(model_path, data=json.dumps(os_model), headers=headers, auth=auth, verify=False)
print("\tResponse: %s" % response)

#######################
#
# Step 7: Search with LTR
#
#######################
# issue a search!
print("Search with baseline")
query_obj = {
    'query': {
        'multi_match': {
            'query': queries[1],
            'fields': ['title^2', 'body']
        }
    },
}
response = client.search(body=query_obj, index=index_name)
print("Response:\n%s" % json.dumps(response, indent=True))
print("Search with LTR")

query_obj["rescore"] = {
    "window_size": 10,
    "query": {
        "rescore_query": {
            "sltr": {
                "params": {
                    "keywords": queries[1]
                },
                "model": model_name,
                # Since we are using a named store, as opposed to simply '_ltr', we need to pass it in
                "store": ltr_store_name,
                "active_features": [title_query_feature_name, body_query_feature_name, price_func_feature_name]
            }
        },
        "rescore_query_weight": "2" # Magic number, but let's say LTR matches are 2x baseline matches
    }
}
response = client.search(body=query_obj, index=index_name)
print("Response:\n%s" % json.dumps(response, indent=True))

# Optional visualization of our tree
model_plot = plot_tree(bst, feat_map_file.name)
model_plot.figure.savefig("ltr_toy_model.png")
# If you are running in an environment other than Gitpod that can display things, you can also uncomment the next line:
# plt.show()