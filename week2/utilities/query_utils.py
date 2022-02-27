import math
# some helpful tools for dealing with queries
def create_stats_query(aggs, extended=True):
    print("Creating stats query from %s" % aggs)
    agg_map = {}
    agg_obj = {"aggs": agg_map, "size": 0}
    stats_type = "stats"
    if extended:
        stats_type = "extended_stats"
    for agg in aggs:
        agg_map[agg] = {stats_type: {"field": agg}}
    return agg_obj

# expects clicks and impressions to be in the row
# Fixing the incorrect assumption
# Let’s illustrate by comparing a popular query with a much less popular query. 
# For a popular head query, you might have the same query millions of times per day compared to a long tail query that executes just a hundred times. 
# If the top document on the long tail query gets clicked 99 out of 100 times, that seems like a way stronger signal of relevance than a head query that gets clicked 1000 times out of million, 
# and yet, if we just pass in clicks alone our model is only going to learn that unadjusted bigger numbers are better.
# Fix: In  \`create_prior_queries_from_group\`, change to \`click_prior_query += "%s^%.3f  " % (item.doc_id, item.clicks/item.num_impressions)\`

def create_prior_queries_from_group(click_group): # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    if click_group is not None:
        for item in click_group.itertuples():
            try:
                click_prior_query += "%s^%.3f  " % (item.doc_id, item.clicks/item.num_impressions)

            except KeyError as ke:
                pass # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query


# expects clicks from the raw click logs, so value_counts() are being passed in
# see create_prior_query_from_group on why change to \`click_prior_query += "%s^%.3f  " % (doc, wgt/query_times_seen)\`
def create_prior_queries(doc_ids, doc_id_weights, query_times_seen): # total impressions isn't currently used, but it mayb worthwhile at some point
    click_prior_query = ""
    # Create a string that looks like:  "query": "1065813^100 OR 8371111^89", where the left side is the doc id and the right side is the weight.  In our case, the number of clicks a document received in the training set
    if doc_ids is not None and doc_id_weights is not None:
        for idx, doc in enumerate(doc_ids):
            try:
                wgt = doc_id_weights[doc]  # This should be the number of clicks or whatever
                click_prior_query += "%s^%.3f  " % (doc, wgt/query_times_seen)
            except KeyError as ke:
                pass # nothing to do in this case, it just means we can't find priors for this doc
    return click_prior_query



def create_simple_baseline(user_query, click_prior_query, filters, sort="_score", sortDir="desc", size=10, include_aggs=True, highlight=True, source=None):

    query_obj = {
        'size': size,
        "sort":[
            {sort: {"order": sortDir}}
        ],
        "query": {

            "bool": {
                "must": [

                ],
                "should":[ #
                    {
                      "match": {
                            "name": {
                                "query": user_query,
                                "fuzziness": "1",
                                "prefix_length": 2, # short words are often acronyms or usually not misspelled, so don't edit
                                "boost": 0.01
                            }
                       }
                    },
                    {
                      "match_phrase": { # near exact phrase match
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
                                       "longDescription^5", "department^0.5", "sku", "manufacturer", "features", "categoryPath"]
                       }
                    },
                    {
                      "terms":{ # Lots of SKUs in the query logs, boost by it, split on whitespace so we get a list
                        "sku": user_query.split(),
                        "boost": 50.0
                      }
                    },
                    { # lots of products have hyphens in them or other weird casing things like iPad
                      "match": {
                            "name.hyphens": {
                                "query": user_query,
                                "operator": "OR",
                                "minimum_should_match": "2<75%"
                            }
                       }
                    }
                ],
                "filter": filters  #
            }

        }
    }
    if click_prior_query != "":
        query_obj["query"]["bool"]["should"].append({
                        "query_string":{  # This may feel like cheating, but it's really not, esp. in ecommerce where you have all this prior data,  You just can't let the test clicks leak in, which is why we split on date
                            "query": click_prior_query,
                            "fields": ["_id"]
                        }
                    })
        #print(query_obj)
    if user_query == "*" or user_query == "#":
        #replace the bool
        try:
            query_obj["query"].pop("bool")
            query_obj["query"] = {"match_all": {}}
        except:
            pass
    if highlight:
        query_obj["highlight"] = {
            "fields": {
                "name": {},
                "shortDescription": {},
                "longDescription": {}
            }
        }
    if source is not None: # otherwise use the default and retrieve all source
        query_obj["_source"] = source

    if include_aggs:
        add_aggs(query_obj)
    return query_obj

# Hardcoded query here.  Better to use search templates or other query config.
def create_query(user_query, click_prior_query, filters, sort="_score", sortDir="desc", size=10, include_aggs=True, highlight=True, source=None):

    query_obj = {
        'size': size,
        "sort":[
            {sort: {"order": sortDir}}
        ],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [

                        ],
                        "should":[ #
                            {
                              "match": {
                                    "name": {
                                        "query": user_query,
                                        "fuzziness": "1",
                                        "prefix_length": 2, # short words are often acronyms or usually not misspelled, so don't edit
                                        "boost": 0.01
                                    }
                               }
                            },
                            {
                              "match_phrase": { # near exact phrase match
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
                                       "longDescription^5", "department^0.5", "sku", "manufacturer", "features", "categoryPath"]
                               }
                            },
                            {
                              "terms":{ # Lots of SKUs in the query logs, boost by it, split on whitespace so we get a list
                                "sku": user_query.split(),
                                "boost": 50.0
                              }
                            },
                            { # lots of products have hyphens in them or other weird casing things like iPad
                              "match": {
                                    "name.hyphens": {
                                        "query": user_query,
                                        "operator": "OR",
                                        "minimum_should_match": "2<75%"
                                    }
                               }
                            }
                        ],
                        "filter": filters  #
                    }
                },
                "boost_mode": "multiply", # how _score and functions are combined
                "score_mode": "sum", # how functions are combined
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
    if click_prior_query != "":
        query_obj["query"]["function_score"]["query"]["bool"]["should"].append({
                        "query_string":{  # This may feel like cheating, but it's really not, esp. in ecommerce where you have all this prior data,  You just can't let the test clicks leak in, which is why we split on date
                            "query": click_prior_query,
                            "fields": ["_id"]
                        }
                    })
        #print(query_obj)
    if user_query == "*" or user_query == "#":
        #replace the bool
        try:
            query_obj["query"].pop("bool")
            query_obj["query"] = {"match_all": {}}
        except:
            pass
    if highlight:
        query_obj["highlight"] = {
            "fields": {
                "name": {},
                "shortDescription": {},
                "longDescription": {}
            }
        }
    if source is not None: # otherwise use the default and retrieve all source
        query_obj["_source"] = source

    if include_aggs:
        add_aggs(query_obj)
    return query_obj


def add_aggs(query_obj):
    query_obj["aggs"] = {
        "department": {
            "terms": {
                "field": "department.keyword",
                "min_doc_count": 1
            }
        },
        "missing_images": {
            "missing": {
                "field": "image"
            }
        },
        "regularPrice": {
            "range": {
                "field": "regularPrice",
                "ranges": [
                    {"key": "$", "to": 100},
                    {"key": "$$", "from": 100, "to": 200},
                    {"key": "$$$", "from": 200, "to": 300},
                    {"key": "$$$$", "from": 300, "to": 400},
                    {"key": "$$$$$", "from": 400, "to": 500},
                    {"key": "$$$$$$", "from": 500},
                ]
            },
            "aggs": {
                "price_stats": {
                    "stats": {"field": "regularPrice"}
                }
            }
        }

    }
