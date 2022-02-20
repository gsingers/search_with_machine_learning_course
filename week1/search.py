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

        # DONE: TODO: IMPLEMENT AND SET filters, display_filters and applied_filters.
        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)

        if agg_type == "range":
            # pass  # DONE: TODO: IMPLEMENT
            agg_from = request.args.get(filter + ".from", filter)
            agg_to = request.args.get(filter + ".to", filter)

            if agg_from:
                applied_filters += "&{}.from={}".format(filter, agg_from)
            if agg_to:
                applied_filters += "&{}.to={}".format(filter, agg_to)

            range_filter = {"range": {filter: {}}}
            display = ""

            minimum = request.args.get(filter + ".from")
            maximum = request.args.get(filter + ".to")

            if minimum:
                range_filter["range"][filter]["gte"] = minimum
                display += f"{minimum} <= "

            display += agg_display_name

            if maximum:
                range_filter["range"][filter]["lt"] = maximum
                display += f" < {maximum} "

            print(f"range_filter: {range_filter}")
            filters.append(range_filter)
            display_filters.append(display)

        elif agg_type == "terms":
            # pass  # DONE: TODO: IMPLEMENT
            agg_key = request.args.get(filter + ".key", filter)
            if agg_key:
                applied_filters += f"&{filter}.key={agg_key}"
                terms_filter = {"terms": {filter + ".keyword": [agg_key]}}
                filters.append(terms_filter)
                display_filters.append(f"{filter} = {agg_key}")

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
    size_results = 25  # Make this smaller in the future (~10)

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
            "fields": [
                "name.shingled^100",
                "name.non_stemmed^90",
                "name^80",
                "manufacturer.shingled^75",
                "manufacturer.non_stemmed^75",
                "manufacturer^75",
                "department.shingled^50",
                "department.non_stemmed^50",
                "department^50",
                "shortDescription.shingled^70",
                "shortDescription.non_stemmed^60",
                "shortDescription^50",
                "longDescription.shingled^40",
                "longDescription.non_stemmed^30",
                "longDescription^20",
                "relatedProducts",
            ],
        }

    # DONE: TODO: "match_all": {}  # Replace me with a query that both searches and filters
    query_obj = {
        "size": size_results,
        "query": {
            "bool": {
                "must": [
                    {
                        query_type: query_dict,
                    }
                ],
                "filter": filters,
            }
        },
        "aggs": {
            # TODO: FILL ME IN
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
