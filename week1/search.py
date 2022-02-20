#
# The main search hooks for the Search Flask application.
#
from urllib import response
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
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter, display_name)

        if type == "range":
            key = request.args.get(filter + ".key", filter)
            FROM = request.args.get(filter + ".from", filter)
            TO = request.args.get(filter + ".to", filter)
            applied_filters += f'''&{filter}.key={key}&{filter}.from={FROM}&{filter}.to={TO}'''
            if FROM and TO: range_filter = {"range": {"regularPrice": { "lt": TO, "gte": FROM }}}
            if FROM and not TO: range_filter = {"range": {"regularPrice": {"gte": FROM}}}
            if TO and not FROM: range_filter = {"range": {"regularPrice": {"lt": TO}}}
            filters.append(range_filter)
            display_filters.append(f"Price: {FROM} TO {TO}")
        elif type == "terms":
            key = request.args.get(filter + ".key", filter)
            applied_filters += f'''&{filter}.key={key}'''
            term_filter = {"term": {"department.keyword": key}}
            filters.append(term_filter)
            display_filters.append(f"Department: {key}")
    # print("Filters: {}".format(filters))

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

    response = opensearch.search(index='bbuy_products', body=query_obj)
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc"):
    # print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))

    multi_match_with_filter = {
        "bool": {
            "must": [{
                    "multi_match": {
                        "query": user_query,
                        "type": "cross_fields",
                        "analyzer": "english",
                        "minimum_should_match": "100%",
                        "fields": [
                            "manufacturer^100",
                            "name^50",
                            "categoryPath^25",
                            "department"
                        ],
                    },
                }],
            "should": [
                {
                    "match_phrase": {
                        "shortDescription": {
                            "query": user_query, "analyzer": "english"
                        }
                    }
                }
            ],
            "filter": filters,
        }
    }

    match_all_with_filter = {
        "bool": {
            "must": [{"match_all": {}}],
            "filter": filters
        }
    }

    match_obj = match_all_with_filter if user_query == '*' else multi_match_with_filter

    query_obj = {
        "query": {
            "function_score": {
                "query": match_obj,
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "salesRankShortTerm",
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
                            "field": "salesRankLongTerm",
                            "modifier": "reciprocal",
                            "missing": 100000000
                        }
                    }
                ],
                "boost_mode": "multiply",
                "score_mode": "avg"
            }
        },
        "from": 0,
        "size": 100,
        "aggregations": {
            "brands": {
                "terms": {
                    "field": "manufacturer.keyword"
                }
            },
            "department": {
                "terms": {
                    "field": "department.keyword"
                }
            },
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": [
                        {
                            "key": "*-100",
                            "to": 100
                        },
                        {
                            "key": "100-200",
                            "from": 100,
                            "to": 200
                        },
                        {
                            "key": "200-500",
                            "from": 200,
                            "to": 500
                        },
                        {
                            "key": "500-1000",
                            "from": 500,
                            "to": 1000
                        },
                        {
                            "key": "1000-2000",
                            "from": 1000,
                            "to": 2000
                        },
                        {
                            "key": "2000-5000",
                            "from": 2000,
                            "to": 5000
                        },
                        {
                            "key": "5000-*",
                            "from": 5000
                        }
                    ]
                }
            },
            "missing_images": {
                "missing": {
                    "field": "image.keyword"
                }
            }
        },
        "_source": [
            "productId",
            "name",
            "categoryPath",
            "image",
            "active",
            "regularPrice",
            "salePrice",
            "onSale",
            "url",
            "shortDescription",
            "department",
            "departmentId",
            "manufacturer"
        ],
        "highlight": {
            "fields": {
                "*": {}
            }
        },
        "sort": [{
            sort: {"order": sortDir}
        }]
    }
    return query_obj
