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


def create_rescore_ltr_query(user_query, ltr_model_name, ltr_store_name, active_features=None, filters=None, size=200, rescore_size=100, include_aggs=True, highlight=True, source=None):
    # Create the base query
    query_obj = create_query(user_query, filters, size=size, include_aggs=include_aggs, highlight=highlight, source=source)
    #add on the rescore
    query_obj["rescore"] = {
        "window_size": rescore_size,
        "query": {
            "rescore_query": {
                "sltr": {
                    "params": {
                        "keywords": user_query
                    },
                    "model": ltr_model_name,
                    # Since we are using a named store, as opposed to simply '_ltr', we need to pass it in
                    "store": ltr_store_name,
                }
            },
            "rescore_query_weight": "2"  # Magic number, but let's say LTR matches are 2x baseline matches
        }
    }
    if active_features is not None and len(active_features) > 0:
        query_obj["rescore"]["query"]["rescore_query"]["sltr"]["active_features"] =  active_features
    return query_obj

# a bit of hack to accentuate the baseline that LTR is learning the features
def create_simple_baseline(user_query, filters,sort="_score", sortDir="desc", size=10, include_aggs=True, highlight=True, source=None):
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
                      "multi_match": {
                            "query": user_query,
                            "type": "phrase",
                            "slop": "6",
                            "boost": 10.0,
                            "minimum_should_match": "2<75%",
                            "fields": ["name^10", "name.hyphens", "shortDescription",
                                       "longDescription", "department", "sku", "manufacturer", "features", "categoryPath"]
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
                                "operator": "AND",
                                "minimum_should_match": "2<75%"
                            }
                       }
                    }
                ],
                "filter": filters  #
            }

        }
    }
    if user_query == "*":
        #replace the bool
        try:
            query_obj["query"]["function_score"]["query"].pop("bool")
            query_obj["query"]["function_score"]["query"] = {"match_all": {}}
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
    return query_obj

# Hardcoded query here.  Better to use search templates or other query config.
def create_query(user_query, filters, sort="_score", sortDir="desc", size=10, include_aggs=True, highlight=True, source=None):
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
                                    "boost": 10.0,
                                    "minimum_should_match": "2<75%",
                                    "fields": ["name^10", "name.hyphens", "shortDescription",
                                               "longDescription", "department", "sku", "manufacturer", "features", "categoryPath"]
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
                                        "operator": "AND",
                                        "minimum_should_match": "2<75%"
                                    }
                               }
                            }
                        ],
                        "filter": filters  #
                    }
                },
                "boost_mode": "multiply",
                "score_mode": "sum",
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
    if user_query == "*":
        #replace the bool
        query_obj["query"]["function_score"]["query"].pop("bool")
        query_obj["query"]["function_score"]["query"] = {"match_all": {}}
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
    return query_obj
