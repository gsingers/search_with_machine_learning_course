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
        #
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter,
                                                                                 display_name)
        #TODO: IMPLEMENT AND SET filters, display_filters and applied_filters.
        # filters get used in create_query below.  display_filters gets used by display_filters.jinja2 and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)
        if type == "range":
            from_val = request.args.get(filter + ".from", None)
            to_val = request.args.get(filter + ".to", None)
            

            range_val = {}
            if from_val:
                range_val["gte"] = from_val
            else:
                from_val = "*"

            if to_val:
                range_val["lte"] = to_val
            else:
                to_val = "*"

            print("from:{}, to:{}".format(from_val, to_val))
            #print(from_val)           
            #print(to_val)           
            

            range_filter = {"range": {filter: range_val}}

            filters.append(range_filter)
            display_filters.append("{} from {} to {}".format(display_name, from_val, to_val))
            applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}&{}.from={}&{}.to={}".format(filter, filter, type, filter,
                                                                                 display_name,filter,from_val,filter,to_val)
        

        elif type == "terms":
            #pass #TODO: IMPLEMENT
            term_field = request.args.get(filter + ".fieldName", filter)
            term_key = request.args.get(filter + ".key", None)
            term_filter = {"term": {term_field: term_key}}
            filters.append(term_filter)
            display_filters.append("{} filtered by {}".format(display_name, term_key))
            applied_filters += "&{}.fieldName={}&{}.key={}".format(field, term_field, filter, term_key)

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
    index_name = 'bbuy_products'
    response = opensearch.search (body=query_obj, index=index_name)
   
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
    if user_query=="*":
        query_obj = {
            'size': 10,
            "query": {
                "match_all": {} 
            }
        }
    else: 
        query_obj = {
            'size': 10,
            "sort": [
                {sort: sortDir}
            ],
            "query": {
                #"match_all": {} # Replace me with a query that both searches and filters
                #"bool": {
                #    "must": [
                #        {"multi_match": {"query": user_query}}
                #    ],
                #    "filter": filters
                #}

                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": user_query,
                                "type": "phrase",
                                "slop": "5",
                                "fields": ["name^10", "shortDescription^5", "longDescription^5", "department^0.5"]
                            }
                        }
                    ],
                    "should":[],
                    "filter": filters  
                }
            },
            "aggs": {
                #TODO: FILL ME IN
                "department": {
                    "terms": {
                        "field": "department.keyword"
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
        }
    return query_obj
