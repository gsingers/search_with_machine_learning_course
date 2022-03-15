#
# The main search hooks for the Search Flask application.
#
from flask import (
    Blueprint, redirect, render_template, request, url_for, current_app
)
from typing import List
from week4.opensearch import get_opensearch

import week4.utilities.query_utils as qu
import week4.utilities.ltr_utils as lu

bp = Blueprint('search', __name__, url_prefix='/search')


def process_filters(filters_input):
    # Filters look like: &filter.name=regularPrice&regularPrice.key={{ agg.key }}&regularPrice.from={{ agg.from }}&regularPrice.to={{ agg.to }}
    filters = []
    display_filters = []  # Also create the text we will use to display the filters that are applied
    applied_filters = ""
    for filter in filters_input:
        type = request.args.get(filter + ".type")
        display_name = request.args.get(filter + ".displayName", filter)
        applied_filters += "&filter.name={}&{}.type={}&{}.displayName={}".format(filter, filter, type, filter,
                                                                                 display_name)
        if type == "range":
            from_val = request.args.get(filter + ".from", None)
            to_val = request.args.get(filter + ".to", None)
            print("from: {}, to: {}".format(from_val, to_val))
            # we need to turn the "to-from" syntax of aggregations to the "gte,lte" syntax of range filters.
            to_from = {}
            if from_val:
                to_from["gte"] = from_val
            else:
                from_val = "*"  # set it to * for display purposes, but don't use it in the query
            if to_val:
                to_from["lt"] = to_val
            else:
                to_val = "*"  # set it to * for display purposes, but don't use it in the query
            the_filter = {"range": {filter: to_from}}
            filters.append(the_filter)
            display_filters.append("{}: {} TO {}".format(display_name, from_val, to_val))
            applied_filters += "&{}.from={}&{}.to={}".format(filter, from_val, filter, to_val)
        elif type == "terms":
            field = request.args.get(filter + ".fieldName", filter)
            key = request.args.get(filter + ".key", None)
            the_filter = {"term": {field: key}}
            filters.append(the_filter)
            display_filters.append("{}: {}".format(display_name, key))
            applied_filters += "&{}.fieldName={}&{}.key={}".format(filter, field, filter, key)
    print("Filters: {}".format(filters))

    return filters, display_filters, applied_filters


def get_query_category(user_query, query_class_model):
    # (('__label__cat02015', '__label__cat02661', '__label__cat02009', '__label__abcat0504005', '__label__cat02003'),
    # array([0.97072554, 0.00247421, 0.00227388, 0.00157165, 0.00152982]))
    prediction = query_class_model.predict(user_query, 5, threshold=0.2)
    prediction = dict(zip(prediction[0], prediction[1]))
    print(prediction)
    return prediction


@bp.route('/query', methods=['GET', 'POST'])
def query():
    opensearch = get_opensearch()
    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"
    model = "simple"
    explain = False
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
        explain_val = request.form.get("explain", "false")
        if explain_val == "true":
            explain = True
        model = request.form.get("model", "simple")
        click_prior = get_click_prior(user_query)

        # incredibly bad results
        # query_obj = qu.create_simple_baseline(user_query, click_prior, [], sort, sortDir, size=100)

        query_obj = {
            "size": 100,
            "query": {
                "bool": {
                    "should": [],
                    "must": [
                        {
                            "multi_match": {
                                "query": user_query,
                                "fields": [
                                    "name^10.0",
                                    "manufacturer^2.0",
                                    "color",
                                    "class^5.0",
                                    "categoryPath^20"
                                ],
                                "type": "cross_fields",
                                "operator": "AND",
                                "slop": 0,
                                "minimum_should_match": "3<80%",
                                "tie_breaker": 0.1,
                                "boost": 1.0
                            }
                        }
                    ]
                }
            },
            "sort": []
        }


    elif request.method == 'GET':  # Handle the case where there is no query or just loading the page
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        explain_val = request.args.get("explain", "false")
        click_prior = get_click_prior(user_query)
        if explain_val == "true":
            explain = True
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)
        query_obj = qu.create_simple_baseline(user_query, click_prior, filters, sort, sortDir, size=100)
    else:
        query_obj = qu.create_query("*", "", [], sort, sortDir, size=100)

    query_class_model = current_app.config["query_model"]

    prediction = get_query_category(user_query, query_class_model)

    CONFIDENCE_THRESHOLD_FILTER = 0.8
    CONFIDENCE_THRESHOLD_BOOST = 0.3
    BOOST_FACTOR = 200.0

    categories_to_filter = [c.removeprefix('__label__') for c in prediction.keys()
                            if prediction[c] > CONFIDENCE_THRESHOLD_FILTER]
    categories_to_boost = [c.removeprefix('__label__') for c in prediction.keys()
                           if prediction[c] > CONFIDENCE_THRESHOLD_BOOST]

    print(f'Filtern mit: {categories_to_filter}')
    print(f'Boosten mit: {categories_to_boost}')

    if categories_to_filter:
        query_obj['query']['bool']['filter'] = {
            "terms": {
                "categoryPathIds": categories_to_filter
            }
        }

    if categories_to_boost:
        query_obj['query']['bool']['should'] = [{
            "terms": {
                "categoryPathIds": categories_to_boost,
                "boost": BOOST_FACTOR
            }}]

    print(query_obj)
    print()
    response = opensearch.search(body=query_obj, index=current_app.config["index_name"], explain=explain)
    # Postprocess results here if you so desire

    # print(response)
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir, model=model, explain=explain,
                               query_category=categories_to_filter)
    else:
        redirect(url_for("index"))


def get_click_prior(user_query):
    click_prior = ""
    if current_app.config.get("priors_gb"):
        try:
            prior_doc_ids = None
            prior_doc_id_weights = None
            query_times_seen = 0  # careful here
            prior_clicks_for_query = None
            prior_clicks_for_query = current_app.config["priors_gb"].get_group(user_query)
            if prior_clicks_for_query is not None and len(prior_clicks_for_query) > 0:
                prior_doc_ids = prior_clicks_for_query.sku.drop_duplicates()
                prior_doc_id_weights = prior_clicks_for_query.sku.value_counts()  # histogram gives us the click counts for all the doc_ids
                query_times_seen = prior_clicks_for_query.sku.count()
                click_prior = qu.create_prior_queries(prior_doc_ids, prior_doc_id_weights, query_times_seen)
        except KeyError as ke:
            pass
            # nothing to do here, we just haven't seen this query before in our training set
    print("prior: %s" % click_prior)
    return click_prior
