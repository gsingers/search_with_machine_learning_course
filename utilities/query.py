# A simple client for querying driven by user input on the command line.  Has hooks for the various
# weeks (e.g. query understanding).  See the main section at the bottom of the file
from opensearchpy import OpenSearch
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import argparse
import json
import os
from getpass import getpass
from urllib.parse import urljoin
import pandas as pd
import fileinput
import logging
import fasttext
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')
category_model = fasttext.load_model('/workspace/datasets/week3/modelfastext_1m_proc25.bin')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# expects clicks and impressions to be in the row
def create_prior_queries_from_group(
        click_group):  # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    if click_group is not None:
        for item in click_group.itertuples():
            try:
                click_prior_query += "%s^%.3f  " % (item.doc_id, item.clicks / item.num_impressions)

            except KeyError as ke:
                pass  # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# expects clicks from the raw click logs, so value_counts() are being passed in
def create_prior_queries(doc_ids, doc_id_weights,
                         query_times_seen):  # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    click_prior_map = ""  # looks like: '1065813':100, '8371111':809
    if doc_ids is not None and doc_id_weights is not None:
        for idx, doc in enumerate(doc_ids):
            try:
                wgt = doc_id_weights[doc]  # This should be the number of clicks or whatever
                click_prior_query += "%s^%.3f  " % (doc, wgt / query_times_seen)
            except KeyError as ke:
                pass  # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# Hardcoded query here.  Better to use search templates or other query config.
def create_query(user_query, 
                click_prior_query, 
                filters, 
                sort="_score", 
                sortDir="desc", 
                size=10, 
                source=None, 
                use_syn=False,
                categories=None,
                boost=False):
    print(categories)
    if use_syn:
        name_field = "name.synonyms"
    else:
        name_field = "name"


    should_clauses = [  #
                        {
                            "match": {
                                name_field: {
                                    "query": user_query,
                                    "fuzziness": "1",
                                    "prefix_length": 2,
                                    # short words are often acronyms or usually not misspelled, so don't edit
                                    "boost": 0.01
                                }
                            }
                        },
                        {
                            "match_phrase": {  # near exact phrase match
                                "name.hyphens": {
                                    "query": user_query,
                                    "slop": 1,
                                    "boost": 50
                                }
                            }
                        },
                        {
                            "multi_match": {
                                "query": user_query,
                                "type": "phrase",
                                "slop": "6",
                                "minimum_should_match": "2<75%",
                                "fields": ["name^10", "name.hyphens^10", "shortDescription^5",
                                            "longDescription^5", "department^0.5", "sku", "manufacturer", "features",
                                            "categoryPath", "name_synonyms"]
                            }
                        },
                        {
                            "terms": {
                                # Lots of SKUs in the query logs, boost by it, split on whitespace so we get a list
                                "sku": user_query.split(),
                                "boost": 50.0
                            }
                        },
                        {  # lots of products have hyphens in them or other weird casing things like iPad
                            "match": {
                                "name.hyphens": {
                                    "query": user_query,
                                    "operator": "OR",
                                    "minimum_should_match": "2<75%"
                                }
                            }
                        }
                    ]

    category_boost = None
    query_filters = filters if filters is not None else [] 
    if categories is not None:
        # if boots is True, will boost the category
        if boost:
            category_boost = {"term":
                                {"categoryPathIds.keywords":categories,
                                 "boost":50.0
                                }
                            }
            should_clauses.append(category_boost)
        #if boost is false we going to filter
        else:
            print("entra for filter")
            query_filter = {"term":
                                {"categoryPathIds.keywords":categories
                                }
                            }
            query_filters.append(query_filter)
            
    query_obj = {
        'size': size,
        "sort": [
            {sort: {"order": sortDir}}
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [],
                        "should": should_clauses,
                        "minimum_should_match": 1,
                        "filter": query_filters  #
                    }
                },
                "boost_mode": "multiply",  # how _score and functions are combined
                "score_mode": "sum",  # how functions are combined
                "functions": [
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankShortTerm"
                            }
                        },
                        "gauss": {
                            "salesRankShortTerm": {
                                "origin": "1.0",
                                "scale": "100"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankMediumTerm"
                            }
                        },
                        "gauss": {
                            "salesRankMediumTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "filter": {
                            "exists": {
                                "field": "salesRankLongTerm"
                            }
                        },
                        "gauss": {
                            "salesRankLongTerm": {
                                "origin": "1.0",
                                "scale": "1000"
                            }
                        }
                    },
                    {
                        "script_score": {
                            "script": "0.0001"
                        }
                    }
                ]

            }
        }
    }
    
    if click_prior_query is not None and click_prior_query != "":
        query_obj["query"]["function_score"]["query"]["bool"]["should"].append({
            "query_string": {
                # This may feel like cheating, but it's really not, esp. in ecommerce where you have all this prior data,  You just can't let the test clicks leak in, which is why we split on date
                "query": click_prior_query,
                "fields": ["_id"]
            }
        })
    if user_query == "*" or user_query == "#":
        # replace the bool
        try:
            query_obj["query"] = {"match_all": {}}
        except:
            print("Couldn't replace query for *")
    if source is not None:  # otherwise use the default and retrieve all source
        query_obj["_source"] = source
    return query_obj

def create_vector_query(user_query, size=10, k=5):
    query_embedding = model.encode([user_query])[0].tolist()
    query_obj = {"size": size,
                "query": {
                    "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": k
                    }
                    }
                }
                }
    print(query_obj)
    return query_obj
                
def search(client, user_query, index="bbuy_products", use_syn=False, min_score=0.5, vector_query=False):
    candidate_k = 5
    print("'{}'".format(user_query))
    cats, scores = category_model.predict(user_query, k=candidate_k)
    
    #filter categories with score higher than min
    categories = [cat.replace('__label__','') for cat, score in zip(cats, scores) if score > min_score]

    if vector_query:
        query_obj = create_vector_query(user_query)
    else:
        query_obj = create_query(user_query, 
                                click_prior_query=None, 
                                filters = None,
                                source=["name", "shortDescription"], 
                                use_syn=use_syn,
                                categories = categories[0] if len(categories) > 0 else None, 
                                )
    logging.info(query_obj)
    response = client.search(query_obj, index=index)
    names = []
    if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
        hits = response['hits']['hits']
        print(json.dumps(response, indent=2))
        

    for hit in response['hits']['hits']:
        print(hit['_source']['name'])

if __name__ == "__main__":
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
    parser = argparse.ArgumentParser(description='Build LTR.')
    general = parser.add_argument_group("general")
    general.add_argument("-i", '--index', default="bbuy_products",
                         help='The name of the main index to search')
    general.add_argument("-s", '--host', default="localhost",
                         help='The OpenSearch host name')
    general.add_argument("-p", '--port', type=int, default=9200,
                         help='The OpenSearch port')
    general.add_argument('--user',
                         help='The OpenSearch admin.  If this is set, the program will prompt for password too. If not set, use default of admin/admin')
    general.add_argument('--synonyms', default=False, action='store_true',
                         help='If True use synonyms in name')
    general.add_argument('--vector_query', default=False, action='store_true',
                         help='If True use approx KNN to search')                         
    args = parser.parse_args()
    output_file = "output.txt"
    featureset_file = "featureset.json"
    if len(vars(args)) == 0:
        parser.print_usage()
        exit()

    host = args.host
    port = args.port
    synonyms = args.synonyms
    vector_query = args.vector_query
    if args.user:
        password = getpass()
        auth = (args.user, password)

    base_url = "https://{}:{}/".format(host, port)
    opensearch = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        # client_cert = client_cert_path,
        # client_key = client_key_path,
        use_ssl=True,
        verify_certs=False,  # set to true if you have certs
        ssl_assert_hostname=False,
        ssl_show_warn=False,

    )
    index_name = args.index
    query_prompt = "\nEnter your query (type 'Exit' to exit or hit ctrl-c):"
    print(query_prompt)
    #for line in input():
    while 1==1:
        line = input()
        query = line.rstrip()
        
        if query == "Exit":
            break
        search(client=opensearch, user_query=query, index=index_name, use_syn=synonyms, vector_query=vector_query)

        

    