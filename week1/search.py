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
            from_value = request.args.get(filter + ".from", None)
            to_value = request.args.get(filter + ".to", None)
            ret_obj = {}

            if from_value and from_value != "*":
                ret_obj["gte"] = from_value
            if to_value and to_value != "*":
                ret_obj["lt"] = to_value

            filter_obj = {"range": {filter: ret_obj}}  
            filters.append(filter_obj)
            if from_value is None or len(from_value) == 0:
                from_value = "*"
            if to_value is None or len(to_value) == 0:
                to_value = "*"
            dsf = "{}: {} TO {}".format(display_name, from_value, to_value)    
            print(f"Display Filter: {dsf}" )    

            display_filters.append(dsf)  
            apf = "&{}.from={}&{}.to={}".format(filter, from_value, filter, to_value)
            print(f"Applied Filter: {apf}")

            applied_filters += apf
        elif type == "terms":
            key = request.args.get(filter + ".key", None)
            term_field_name = request.args.get(filter + ".esFieldName", filter)
            filter_obj = {"term": {term_field_name: key}}
            print(filter_obj)

            filters.append(filter_obj)
            dsf = "{}: {}".format(display_name, key)
            display_filters.append(dsf)
            apf = "&{}.esFieldName={}&{}.key={}".format(filter, term_field_name, filter, key)
            applied_filters +=  apf

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
    pageNo = 0
    pageSize = 10
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
        query_obj = create_query(user_query, [], sort, sortDir, pageNo, pageSize)
    elif request.method == 'GET':  # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        pageSize = int(request.args.get("pageSize", pageSize))
        pageNo = int(request.args.get("pageNo", pageNo))
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)

        query_obj = create_query(user_query, filters, sort, sortDir, pageNo, pageSize)
    else:
        query_obj = create_query("*", [], sort, sortDir, pageNo, pageSize)

    print("query obj: {}".format(query_obj))
    response = None   # TODO: Replace me with an appropriate call to OpenSearch
    # Postprocess results here if you so desire
    try:
        response = opensearch.search(body=query_obj, index="bbuy_products")
    except Exception as e:
        print(error)
        error = e

    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir, pageSize=pageSize, pageNo=pageNo)
    else:
        redirect(url_for("query"))


def create_query(user_query, filters, sort="_score", sortDir="desc", pageNo=0, pageSize=10):
    print("Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))
    query_obj = {       
        "sort": [
            {sort: {"order": sortDir}}
        ],
        "from": pageSize * pageNo,
        "size": pageSize,
        "query": {
            "function_score":{
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
                "score_mode": "avg",            
                "query":{
                    "bool":{
                        "should": [
                            {
                                "multi_match": {
                                    'boost' : 50,
                                    'query': user_query,
                                    'type':'phrase',
                                    'slop' : 5,
                                    "fields": ["name^100", "shortDescription^50", "longDescription^10", "department"]
                                }
                            },
                            {
                                "match": {
                                    "name":{
                                        'query': user_query,
                                        'boost': 10,
                                        'minimum_should_match': '75%'
                                    }
                                }
                            },                            
                            { # work little bit like auto complete
                                "match_phrase_prefix":{
                                    "name":{
                                        "query": user_query,
                                        "boost":1
                                    }
                                }
                            }
                        ],
                        "minimum_should_match":1,
                        "filter": filters
                    }
                }
            }

            # Replace me with a query that both searches and filters
            
        },
        "aggs": {
            #TODO: FILL ME IN
            "department":{
                "terms":{
                    "field": "department.keyword"
                }
            },
            "regularPrice":{
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
                }                
            },
            "missing_images":{
                "missing":{
                    "field": "image.keyword"
                }
            }

        }
    }
    if user_query == "*":
        query_obj["query"]["function_score"]["query"]["bool"]["should"] = [{"match_all": {}}]
    return query_obj
