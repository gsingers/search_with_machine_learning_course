#
# The main search hooks for the Search Flask application.
#
from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from week1.opensearch import get_opensearch

bp = Blueprint('search', __name__, url_prefix='/search')


# Process the filters requested by the user and return a tuple that is appropriate for use in: the query, URLs displaying the filter and the display of the applied filters
# filters -- convert the URL GET structure into an OpenSearch filter query
# display_filters -- return an array of filters that are applied that is appropriate for display
# applied_filters -- return a String that is appropriate for inclusion in a URL as part of a query string.  This is basically the same as the input query string
def process_filters(filters_input):
    # Filters look like: &filter.name=regularPrice&regularPrice.key={{ agg.key }}&regularPrice.from={{ agg.from }}&regularPrice.to={{ agg.to }}
    filters = []
    display_filters = []  # Also create the text we will use to display the filters that are applied
    applied_filters = ""
    for filter in filters_input:
        type = request.args.get(filter + ".type")
        display_name = request.args.get(filter + ".displayName", filter)
        key = request.args.get(filter + ".key")

        #
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}&{}.key={}".format(filter, filter, type, filter,
                                                                                           display_name, filter, key)
        # TODO: IMPLEMENT AND SET filters, display_filters and applied_filters.

        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)

        search_filter = {}
        if type == "range":
            range_filter = {}

            from_filter = request.args.get(filter + ".from") if request.args.get(filter + ".from") else 0
            to_filter = request.args.get(filter + ".to")

            range_filter['gte'] = from_filter
            display = f'{from_filter}'

            if to_filter:
                range_filter['lt'] = to_filter
                display = f'{display} to {to_filter}'

            search_filter = {"range": {filter: range_filter}}

            display_filters.append(f'{display_name}: {display}')

            applied_filters += f'&{filter}.from={from_filter}&{filter}.to={to_filter}'

        elif type == "term":
            search_filter = {"term": {filter + ".keyword": key}}
            display_filters.append(f'{display_name}: {key}')

        filters.append(search_filter)
    print("Filters: {}".format(filters))

    return filters, display_filters, applied_filters


# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_opensearch()  # Load up our OpenSearch client from the opensearch.py file.
    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"
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

        print(f"input filters - {filters_input}")

        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)

        query_obj = create_query(user_query, filters, sort, sortDir)
    else:
        query_obj = create_query("*", [], sort, sortDir)

    print("query obj: {}".format(query_obj))

    response = get_opensearch().search(
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
    if filters is None:
        filters = []
    print("Query: {} Filters: {} Sort: {} sortDir: {}".format(user_query, filters, sort, sortDir))

    searchQuery = _get_search_query_(user_query, filters)
    query_obj = {
        'size': 10,
        # Replace me with a query that both searches and filters
        "query": searchQuery,
        "aggs": {
            "missing_images": {
                "missing": {
                    "field": "image"
                }
            },
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": [
                        {
                            "to": 100,
                            "key": "$"
                        },
                        {
                            "from": 100,
                            "to": 200,
                            "key": "$$"
                        },
                        {
                            "from": 200,
                            "to": 300,
                            "key": "$$$"
                        },
                        {
                            "from": 300,
                            "to": 400,
                            "key": "$$$$"
                        },
                        {
                            "from": 400,
                            "key": "$$$$$"
                        }
                    ]
                }
            },
            "department": {
                "terms": {
                    "field": "department.keyword"
                }
            }
        },
        "sort": {sort: sortDir},
        "_source": ["productId", "name", "shortDescription", "longDescription", "department",
                    "salesRankShortTerm", "salesRankMediumTerm", "salesRankLongTerm", "regularPrice", "image"]
    }
    return query_obj


def _get_search_query_(user_query, filters=[]):
    return {
        "bool": {
            "must": [
                {
                    "function_score": {
                        "query": {
                            "simple_query_string": {
                                "query": user_query,
                                "fields": ["name^1000", "shortDescription^50", "longDescription^10", "department"]
                            }
                        },
                        "boost_mode": "replace",
                        "score_mode": "avg",
                        "functions": [
                            {
                                "field_value_factor": {
                                    "field": "salesRankLongTerm",
                                    "modifier": "reciprocal",
                                    "missing": 100000000
                                }
                            },
                            {
                                "field_value_factor": {
                                    "field": "salesRankMediumTerm",
                                    "modifier": "reciprocal",
                                    "missing": 100000000
                                }
                            },
                            {
                                "field_value_factor": {
                                    "field": "salesRankShortTerm",
                                    "modifier": "reciprocal",
                                    "missing": 100000000
                                }
                            }
                        ]
                    }
                }
            ],
            "filter": filters
        }
    }
