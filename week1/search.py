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
    applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter, display_name)
    for filter in filters_input:
        type = request.args.get(filter + ".type")
        display_name = request.args.get(filter + ".displayName", filter)
        #
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter,
                                                                                 display_name)
        #TODO: IMPLEMENT AND SET filters, display_filters and applied_filters.
        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)
        if type == "range":
            agg_key = request.args.get(filter + ".key")
            agg_from = request.args.get(filter + ".from")
            agg_to = request.args.get(filter + ".to")

            rangeFilter = {}
            if agg_from != "":
                rangeFilter["gte"] = agg_from
            if agg_to != "":
                rangeFilter["lte"] = agg_to

            filters.append({
                "range": {
                    "regularPrice": rangeFilter
                }
            })

            applied_filters += "&regularPrice.key={}&regularPrice.from={}&regularPrice.to={}".format(
                agg_key, agg_from, agg_to)
            display_filters.append("{} {}".format(display_name, agg_key))
        elif type == "terms":
            #pass #TODO: IMPLEMENT
            agg_key = request.args.get(filter + ".key")
            filters.append({
                "term": {
                    "department.keyword": agg_key
                }
            })

            applied_filters += "&department.key={}".format(agg_key)
            display_filters.append("{} {}".format(display_name, agg_key))

    print("Filters: {}".format(filters))

    return filters, display_filters, applied_filters


# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_opensearch() # Load up our OpenSearch client from the opensearch.py file.
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
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)

        query_obj = create_query(user_query, filters, sort, sortDir)
    else:
        query_obj = create_query("*", [], sort, sortDir)

    print("query obj: {}".format(query_obj))
    #response = None   # TODO: Replace me with an appropriate call to OpenSearch
    # Postprocess results here if you so desire
    response = opensearch.search(
        body=query_obj,
        index="bbuy_products"
    )

    #print(response)
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc"):
    print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))

    queries = []
    if user_query == "*":
        queries.append({"match_all": {}})
    else:
        queries.append({
            "function_score": {
            "query": {
              "query_string": {
                "query": user_query,
                "fields": [
                  "name^100",
                  "shortDescription^50",
                  "longDescription^10",
                  "department"
                ]
              }
            },
            "boost_mode": "multiply",
            "score_mode": "avg"
          }
        })

    query_obj = {
        'size': 10,
        "_source": ["productId", "name", "shortDescription", "longDescription", "department", "salesRankShortTerm",  "salesRankMediumTerm",  "regularPrice", "image"],
        "query": {
            "bool": {
                "must": queries,
                "filter": filters
            }
        },
        "aggs": {
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": [
                        {
                            "key": "$",
                            "to": 10
                        },
                        {
                            "key": "$$",
                            "from": 10,
                            "to": 100
                        },
                        {
                            "key": "$$$",
                            "from": 100,
                            "to": 1000
                        },
                        {
                            "key": "$$$$",
                            "from": 1000,
                            "to": 5000
                        },
                        {
                            "key": "$$$$$",
                            "from": 5000
                        }
                    ]
                }
            },
            "department": {
                "terms": {
                    "field": "department.keyword",
                    "size": 10
                }
            },
            "missing_images": {
                "missing": {
                    "field": "image.keyword"
                }
            }
        }
    }

    #print(json.dumps(query_obj))

    return query_obj