#
# The main search hooks for the Search Flask application.
#
from flask import (
    Blueprint, redirect, render_template, request, url_for, current_app
)

from week4.opensearch import get_opensearch

import week4.utilities.query_utils as qu
import week4.utilities.ltr_utils as lu

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
    print("IMPLEMENT ME: get_query_category")
    return None


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
    # TODO: Make these parameters
    ltr_store_name = "week2"
    ltr_model_name = "ltr_model"
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

        if model == "simple_LTR":
            query_obj = qu.create_simple_baseline(user_query, click_prior, [], sort, sortDir, size=500)  # We moved create_query to a utility class so we could use it elsewhere.
            query_obj = lu.create_rescore_ltr_query(user_query, query_obj, click_prior, ltr_model_name, ltr_store_name,
                                                    rescore_size=500, main_query_weight=0)
            print("Simple LTR q: %s" % query_obj)
        elif model == "ht_LTR":
            query_obj = qu.create_query(user_query, click_prior, [], sort, sortDir, size=500)  # We moved create_query to a utility class so we could use it elsewhere.
            query_obj = lu.create_rescore_ltr_query(user_query, query_obj, click_prior, ltr_model_name, ltr_store_name,
                                                    rescore_size=500, main_query_weight=0)
            print("LTR q: %s" % query_obj)
        elif model == "hand_tuned":
            query_obj = qu.create_query(user_query, click_prior, [], sort, sortDir, size=100)  # We moved create_query to a utility class so we could use it elsewhere.
            print("Hand tuned q: %s" % query_obj)
        else:
            query_obj = qu.create_simple_baseline(user_query, click_prior, [], sort, sortDir, size=100)  # We moved create_query to a utility class so we could use it elsewhere.
            print("Plain ol q: %s" % query_obj)
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
        model = request.args.get("model", "simiple")
        if model == "simple_LTR":
            query_obj = qu.create_simple_baseline(user_query, click_prior, filters, sort, sortDir, size=500)
            query_obj = lu.create_rescore_ltr_query(user_query, query_obj, click_prior, ltr_model_name, ltr_store_name, rescore_size=500)
        elif model == "ht_LTR":
            query_obj = qu.create_query(user_query, click_prior, filters, sort, sortDir, size=100)
            query_obj = lu.create_rescore_ltr_query(user_query, query_obj, click_prior, ltr_model_name, ltr_store_name, rescore_size=100)
        elif model == "hand_tuned":
            query_obj = qu.create_query(user_query, click_prior, filters, sort, sortDir, size=100)
        else:
            query_obj = qu.create_simple_baseline(user_query, click_prior, filters, sort, sortDir, size=100)
    else:
        query_obj = qu.create_query("*", "", [], sort, sortDir, size=100)

    query_class_model = current_app.config["query_model"]
    query_category = get_query_category(user_query, query_class_model)
    if query_category is not None:
        print("IMPLEMENT ME: add this into the filters object so that it gets applied at search time.  This should look like your `term` filter from week 1 for department but for categories instead")
    #print("query obj: {}".format(query_obj))
    response = opensearch.search(body=query_obj, index=current_app.config["index_name"], explain=explain)
    # Postprocess results here if you so desire

    #print(response)
    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir, model=model, explain=explain, query_category=query_category)
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


