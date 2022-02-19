#
# The main search hooks for the Search Flask application.
#
from operator import index
from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from week1.opensearch import get_opensearch

bp = Blueprint('search', __name__, url_prefix='/search')

PRODUCTS_INDEX = "bbuy_products"
QUERIES_INDEX = "bbuy_queries"
RESPONSE_SIZE = 10

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
        key = request.args.get(filter + ".key")
        #
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}&{}.key={}".format(filter, filter, type, filter,
                                                                                           display_name, filter, key)

        if type == "range":
            to_filter = request.args.get(
                filter + ".to") if request.args.get(filter + ".to") else None
            from_filter = request.args.get(
                filter + ".from") if request.args.get(filter + ".from") else 0
            if to_filter is None:
                filters.append({
                    "range": {
                        filter: {
                            "gte": from_filter
                        }
                    }
                })
            else:
                filters.append({
                    "range": {
                        filter: {
                            "lt": to_filter,
                            "gte": from_filter
                        }
                    }
                })
            display_filters.append(
                f"Fetching all with {filter} in range from {from_filter} to {to_filter}")
            applied_filters += f"&{filter}.to={to_filter}&{filter}.from={from_filter}"
        elif type == "term":
            filters.append({
                "term": {
                    filter: key
                }
            })
            display_filters.append(
                f"Fetching all with {filter} as {key}")  # TODO: IMPLEMENT
    print("Filters: {}".format(filters))

    return filters, display_filters, applied_filters

@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_opensearch()
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"
    pageNo = int(request.args.get("pageNo")
                 ) if request.args.get("pageNo") else 0
    pageSize = int(request.args.get("pageSize")
                   ) if request.args.get("pageSize") else 10
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
    elif request.method == 'GET':
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)
        query_obj = create_query(
            user_query, filters, sort, sortDir,  pageSize, pageNo)
    else:
        query_obj = create_query("*", [], sort, sortDir, pageSize, pageNo)

    print("query obj: {}".format(query_obj))
    search_response = opensearch.search(body=query_obj, index=PRODUCTS_INDEX)
    search_response = process_response(search_response)
    autosuggest_response = get_suggestion(user_query)

    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=search_response, autosuggest_response=autosuggest_response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir, pageNo=pageNo, pageSize=pageSize)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc", pageSize=10, pageNo=0):
    facets = get_facets()
    if (user_query == "*"):
        query = {
            "match_all": {},
        }
    else:
        query = {
            "multi_match": {
                "query": user_query,
                "fields": ["name^100", "shortDescription^50", "longDescription^10", "department"]
            }
        }

    query_function = {
        "function_score": {
            "query": {
                "bool": {
                    "must": [
                        query
                    ],
                    "filter": filters
                }
            },
            "boost_mode": "multiply",
            "score_mode": "avg",
            "functions": [
                {
                    "field_value_factor": {
                        "field": "salesRankLongTerm",
                        "missing": 100000000,
                        "modifier": "reciprocal"
                    }
                },
                {
                    "field_value_factor": {
                        "field": "salesRankMediumTerm",
                        "missing": 100000000,
                        "modifier": "reciprocal"
                    }
                },
                {
                    "field_value_factor": {
                        "field": "salesRankShortTerm",
                        "missing": 100000000,
                        "modifier": "reciprocal"
                    }
                }
            ]
        }
    }
    return {
        'size': RESPONSE_SIZE,
        "from": pageSize * pageNo,
        "track_total_hits": True,
        "query": query_function,
        "aggs": get_facets(),
        "sort": get_sort(sort, sortDir)
    }


def process_response(response):
    products_response = {
        "query_time": response['took'],
        "total_results": response['hits']['total']['value'],
        "products": response['hits']['hits'],
        "aggregations": response['aggregations']
    }
    return products_response


def get_sort(sort, sortDir):
    return [
        {
            sort: {
                "order": sortDir
            }
        }
    ]


def get_facets():
    return {
        "departments": {
            "terms": {
                "field": "department",
            }
        },
        "missing_images": {
            "missing": {
                "field": "image.keyword"
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
                    {"key": "$$$$$$", "from": 500}
                ]
            },
            "aggs": {
                "price_stats": {
                    "stats": {"field": "regularPrice"}
                }
            }
        }
    }


def get_suggestion(term):
    if term == "*":
        return ""
    opensearch = get_opensearch()
    query = {
        "suggest": {
            "autocomplete": {
                "prefix": term,
                "completion": {
                    "field": "text_entry"
                }
            }
        }
    }
    autosuggest_response = opensearch.search(body=query, index=QUERIES_INDEX)
    if autosuggest_response['suggest']['autocomplete'][0]['options'][0]['text']:
        return autosuggest_response['suggest']['autocomplete'][0]['options'][0]['text']
    else:
        return ""
