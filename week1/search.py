#!/usr/bin/env python

#
# The main search hooks for the Search Flask application.
#
from flask import Blueprint, redirect, render_template, request, url_for

from week1.opensearch import get_opensearch

bp = Blueprint("search", __name__, url_prefix="/search")


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
        agg_type = request.args.get(filter + ".type")
        agg_display_name = request.args.get(filter + ".displayName", filter)

        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += f"&filter.name={filter}&{filter}.type={agg_type}&{filter}"
        applied_filters += f".displayName={agg_display_name}"
        # TODO: IMPLEMENT AND SET filters, display_filters and applied_filters.
        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)
        if agg_type == "range":
            pass
        elif agg_type == "terms":
            pass  # TODO: IMPLEMENT

    print(f"Filters: {filters}")

    return filters, display_filters, applied_filters


# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route("/query", methods=["GET", "POST"])
def query():
    # Load up our OpenSearch client from the opensearch.py file.
    opensearch_client = get_opensearch()

    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"
    size_results = 25 # Make this smaller in the future (~10)

    if request.method == "POST":  # a query has been submitted
        user_query = request.form["query"]
        if not user_query:
            user_query = "*"
        sort = request.form["sort"]
        if not sort:
            sort = "_score"
        sortDir = request.form["sortDir"]
        if not sortDir:
            sortDir = "desc"
        query_obj = create_query(user_query, [], sort, sortDir, size_results)
    elif request.method == "GET":
        # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)

        query_obj = create_query(user_query, filters, sort, sortDir, size_results)
    else:
        query_obj = create_query("*", [], sort, sortDir, size_results)

    print(f"query obj: {query_obj}")

    # DONE: TODO: Replace me with an appropriate call to OpenSearch

    index_name_products = "bbuy_products"
    response = opensearch_client.search(body=query_obj, index=index_name_products)

    # Postprocess results here if you so desire

    # print(response)
    if error is None:
        return render_template(
            "search_results.jinja2",
            query=user_query,
            search_response=response,
            display_filters=display_filters,
            applied_filters=applied_filters,
            sort=sort,
            sortDir=sortDir,
            size_results=size_results,
        )
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc", size_results=10):

    print(f"Query: {user_query} Filters: {filters} Sort: {sort}")

    if user_query.strip() == "*":
        # Select all / match all
        query_type = "match_all"
        query_dict = {}
    else:
        query_type = "multi_match"
        query_dict = {
            "query": user_query,
            "fields": ["name^100", "shortDescription^25", "longDescription^10", "relatedProducts"],
        }

    query_obj = {
        "size": size_results,
        "query": {
            # DONE: TODO: "match_all": {}  # Replace me with a query that both searches and filters
            query_type: query_dict
        },
        "aggs": {
            # TODO: FILL ME IN
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": [
                        {
                            "to": 10,
                        },
                        {
                            "from": 10,
                            "to": 50,
                        },
                        {
                            "from": 50,
                            "to": 100,
                        },
                        {
                            "from": 100,
                        },
                    ],
                }
            },
            "department": {
                "terms": {
                    "field": "department.keyword",
                    "size": 20,
                    "missing": "N/A",
                    "min_doc_count": 0,
                }
            },
            "missing_images": {"missing": {"field": "image.keyword"}},
        },
    }

    return query_obj
