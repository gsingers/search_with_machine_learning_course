#
# The main search hooks for the Search Flask application.
#
from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from week1.opensearch import get_opensearch

from json import dumps

bp = Blueprint('search', __name__, url_prefix='/search')


# Process the filters requested by the user and return a tuple that is appropriate for use in: the query, URLs displaying the filter and the display of the applied filters
# filters -- convert the URL GET structure into an OpenSearch filter query
# display_filters -- return an array of filters that are applied that is appropriate for display
# applied_filters -- return a String that is appropriate for inclusion in a URL as part of a query string.  This is basically the same as the input query string
def process_filters(filters_input):
    # Filters look like: &filter.name=regularPrice&regularPrice.key={{ agg.key }}&regularPrice.from={{ agg.from }}&regularPrice.to={{ agg.to }}
    filters = []
    # Also create the text we will use to display the filters that are applied
    display_filters = []
    applied_filters = ""
    for filter in filters_input:
        type = request.args.get(filter + ".type")
        display_name = request.args.get(filter + ".displayName", filter)
        #
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter,
                                                                                 display_name)
        # TODO: IMPLEMENT AND SET filters, display_filters and applied_filters.
        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)
        if type == "range":
            # Example:
            # "filter": [
            #     { "range": { "publish_date": { "gte": "2015-01-01" }}}
            # ]
            filter_key = {}
            if request.args.get(filter + ".from"):
                filter_key["gte"] = request.args.get(filter + ".from")
            if request.args.get(filter + ".to"):
                filter_key["lte"] = request.args.get(filter + ".to")
            if filter_key:
                range_filter_name = {}
                range_filter_name[filter] = filter_key
                range_filter = {"range": range_filter_name}
                filters.append(range_filter)
            pass
        elif type == "terms":
            # "filter": [
            #     { "term":  { "status": "published" }}
            # ]
            pass  # TODO: IMPLEMENT
    print("Filters: {}".format(filters))

    return filters, display_filters, applied_filters


# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route('/query', methods=['GET', 'POST'])
def query():
    # Load up our OpenSearch client from the opensearch.py file.
    opensearch = get_opensearch()
    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = []
    sort = "_score"
    sortDir = "desc"

    print("request.args")
    print(dumps(request.args, indent=4, sort_keys=True))

    if request.method == 'POST':  # a query has been submitted
        user_query = request.form['query']
        if not user_query:
            user_query = "*"
        sort = request.form["sort"]
        if not sort:
            sort = "_score"
        sortDir = request.form["sortDir"]
        if not sortDir:
            sortDir = "desc"
        query_obj = create_query(user_query, [], sort, sortDir)
    elif request.method == 'GET':  # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)

        query_obj = create_query(user_query, filters, sort, sortDir)
    else:
        query_obj = create_query("*", [], sort, sortDir)

    print("query obj: {}".format(query_obj))
    response = opensearch.search(
        body=query_obj,
        index="bbuy_products"
    )
    # Postprocess results here if you so desire

    # print(response)
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc"):
    print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))
    bool_query = {
        "should": [
            {
                "query_string": {
                    "query": user_query,
                    "type": "phrase",
                    "fields": ["name^10", "name.hyphens^10", "shortDescription^5",
                               "longDescription^5", "department^0.5", "sku", "manufacturer", "features", "categoryPath"]
                }
            }
        ]
    }
    if filters:
        bool_query['filter'] = filters
    query_obj = {
        'size': 10,
        "query": {
            "function_score": {
                "query": {
                    "bool": bool_query
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
        },
        "aggs": {
            "class": {
                "terms": {
                    "field": "class.keyword"
                }
            },
            "department": {
                "terms": {
                    "field": "department.keyword"
                }
            },
            "type": {
                "terms": {
                    "field": "type.keyword"
                }
            },
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": [
                        {"key": "$", "to": 100.0},
                        {"key": "$$", "from": 100.0, "to": 200.0},
                        {"key": "$$$", "from": 200.0, "to": 300.0},
                        {"key": "$$$$", "from": 300.0, "to": 400.0},
                        {"key": "$$$$$", "from": 400.0, "to": 500.0},
                        {"key": "$$$$$$", "from": 500.0}
                    ]
                }
            },
            "missing_images": {
                "missing": {
                    "field": "image.keyword"
                }
            }
        }
    }
    return query_obj
