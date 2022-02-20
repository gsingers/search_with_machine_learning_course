#
# The main search hooks for the Search Flask application.
#
from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from week1.opensearch import get_opensearch

bp = Blueprint('search', __name__, url_prefix='/search')

INDEX_NAME = 'bbuy_products'


# Process the filters requested by the user and return a tuple that is appropriate for use in: the query, URLs displaying the filter and the display of the applied filters
# filters -- convert the URL GET structure into an OpenSearch filter query
# display_filters -- return an array of filters that are applied that is appropriate for display
# applied_filters -- return a String that is appropriate for inclusion in a URL as part of a query string.  This is basically the same as the input query string
def process_filters(filters_input):
    # Filters look like: &filter.name=regularPrice&regularPrice.key={{ agg.key }}&regularPrice.from={{ agg.from }}&regularPrice.to={{ agg.to }}
    filters = []
    display_filters = []  # Also create the text we will use to display the filters that are applied
    applied_filters = ""
    for filter_ in filters_input:
        filter_type = request.args.get(filter_ + ".type")
        filter_key = request.args.get(filter_ + ".key")
        display_name = request.args.get(filter_ + ".displayName", filter_)
        from_value = request.args.get(filter_ + '.from')
        to_value = request.args.get(filter_ + '.to')
        #
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += f"&filter.name={filter_}&{filter_}.type={filter_type}&{filter_}.displayName={display_name}&{filter_}.key={filter_key}&{filter_}.from={from_value}&{filter_}.to={to_value}"

        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)
        if filter_type == "range":
            display_filters.append(f'{display_name}: from {from_value} to {to_value}')
            filters.append({
                "range": {
                    filter_: {
                        "gte": from_value,
                        "lte": to_value
                    }
                }
            })
        elif filter_type == "terms":
            display_filters.append(f'{display_name}: {filter_key}')
            filters.append({
                "term": {
                    f'{filter_}.keyword': filter_key
                }
            })
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

    response = opensearch.search(
        body=query_obj,
        index=INDEX_NAME
    )

    # Postprocess results here if you so desire

    #print(response)
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc"):
    print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))
    if user_query and user_query != '*':
        match = {
            "function_score": {
                "query": {
                "query_string": {
                            "query": f"\"{user_query}\"",
                            "fields": ["name^1000", "shortDescription^50", "longDescription^10", "department",  "manufacturer"]
                    }
                },
                "boost_mode": "replace",
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
    else:
        match = {
            "match_all": {

            }
        }

    bool_query = {
        "bool": {
            "must": [match],
            "filter": filters
        }
    }

    query_obj = {
        'size': 10,
        "query": bool_query,
        "sort": {
            sort: sortDir
        },
        "aggs": {
            "regularPrice": {
                "range": {
                    "field": "regularPrice",
                    "ranges": [
                        {
                            "from": 0,
                            "to": 100
                        },
                        {
                            "from": 100,
                            "to": 200
                        },
                        {
                            "from": 200,
                            "to": 300
                        },
                        {
                            "from": 300,
                            "to": 400
                        },
                        {
                            "from": 400,
                            "to": 500
                        },
                        {
                            "from": 500
                        }
                    ]
                }
            },

            "department_agg": {
                "terms": {
                    "field": "department.keyword",
                    "size": 10
                }
            },

            "missing_images": {
                "missing": {
                    "field": "image"
                }
            }
        }
    }
    return query_obj
