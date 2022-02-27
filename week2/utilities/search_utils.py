# Some handy utilities for dealing with searches

import json

import query_utils as qu
import ltr_utils as lu
from opensearchpy import NotFoundError
import pandas as pd
import os


# Given a Test DataFrame, run the queries against the OpenSearch


def evaluate_test_set(test_data, prior_clicks_df, opensearch, xgb_model_name, ltr_store, index, num_queries=100,
                      size=500, rescore_size=500, precision=10, main_query_weight=1, rescore_query_weight=2):
    # (ranks_df, features_df) = data_prepper.get_judgments(test_data, True) # judgments as a Pandas DataFrame
    if precision > size:
        print("Precision can't be greater than the fetch size, changing the precision to be same as size")
        precision = size
    test_data = test_data.sample(frac=1).reset_index(drop=True)  # shuffle things
    query_gb = test_data.groupby("query", sort=False) #small
    prior_clicks_gb = prior_clicks_df.groupby(["query"]) #large
    source = ["sku", "name"]

    no_simple = []
    no_ltr_simple = []
    no_hand_tuned = []
    no_ltr_hand_tuned = []
    no_results = {"simple": no_simple, "ltr_simple": no_ltr_simple, "hand_tuned": no_hand_tuned, "ltr_hand_tuned": no_ltr_hand_tuned}
    # Build a data frame
    q = []
    sku = [] #
    rank = []
    type = []
    score = []
    found = [] # boolean indicating whether this result was a match or not
    new = [] # boolean indicating whether this query was in the training set or not
    results = {"query": q, "sku": sku, "rank": rank, "type": type, "found": found, "new": new, "score": score}

    print("Running %s test queries." % num_queries)
    ctr = 0

    for key in query_gb.groups.keys():
        if ctr >= num_queries:
            print("We've executed %s queries. Finishing." % ctr)
            break
        if ctr % 50 == 0:
            print("Progress[%s]: %s" % (ctr, key))
        ctr += 1
        test_clicks_for_query = query_gb.get_group(key) # this is the set of docs in our test set that have clicks
        # this is the set of skus that were clicked w/o dupes
        # since we are using prior clicks to learn from and boost, we cannot use them for judgment
        test_skus_for_query = test_clicks_for_query.sku.drop_duplicates()
        prior_doc_ids = None
        prior_doc_id_weights = None
        query_times_seen = 0 # careful here
        prior_clicks_for_query = None
        seen = False
        try:
            prior_clicks_for_query = prior_clicks_gb.get_group(key)
            if prior_clicks_for_query is not None and len(prior_clicks_for_query) > 0:
                prior_doc_ids = prior_clicks_for_query.sku.drop_duplicates()
                prior_doc_id_weights = prior_clicks_for_query.sku.value_counts() # histogram gives us the click counts for all the doc_ids
                query_times_seen = prior_clicks_for_query.sku.count()
                seen = True
        except KeyError as ke:
            # nothing to do here, we just haven't seen this query before in our training set
            pass

        click_prior_query = qu.create_prior_queries(prior_doc_ids, prior_doc_id_weights, query_times_seen)
        simple_query_obj = qu.create_simple_baseline(key, click_prior_query, filters=None, size=size, highlight=False, include_aggs=False, source=source)
        # don't care about no results here
        __judge_hits(test_skus_for_query, index, key, no_simple, opensearch, simple_query_obj, "simple", results, seen)
        # Run hand-tuned
        hand_tuned_query_obj = qu.create_query(key, click_prior_query, filters=None, size=size, highlight=False, include_aggs=False, source=source)

        __judge_hits(test_skus_for_query, index, key, no_hand_tuned, opensearch, hand_tuned_query_obj, "hand_tuned", results, seen)
        # NOTE: very important, we cannot look at the test set for click weights, but we can look at the train set.

        ltr_simple_query_obj = lu.create_rescore_ltr_query(key, simple_query_obj, click_prior_query, xgb_model_name, ltr_store, rescore_size=rescore_size,
                                                           main_query_weight=main_query_weight, rescore_query_weight=rescore_query_weight)
        #print(json.dumps(ltr_simple_query_obj))
        __judge_hits(test_skus_for_query, index, key, no_ltr_simple, opensearch, ltr_simple_query_obj, "ltr_simple", results, seen)
        ltr_hand_query_obj = lu.create_rescore_ltr_query(key, hand_tuned_query_obj, click_prior_query, xgb_model_name, ltr_store,
                                                         rescore_size=rescore_size, main_query_weight=main_query_weight, rescore_query_weight=rescore_query_weight)
        __judge_hits(test_skus_for_query, index, key, no_ltr_hand_tuned, opensearch, ltr_hand_query_obj, "ltr_hand_tuned", results, seen)

    return pd.DataFrame(results), no_results


def write_diffs(to_compare_set, to_compare_results, ltr_results, ltr_set, od):
    diff = to_compare_set.symmetric_difference(ltr_set)
    if len(diff) > 0:
        od.write("\tQuery diffs: %s\n" % diff)
    for key in to_compare_results.keys():
        od.write("\tQuery: %s\n" % key)
        base_matches = to_compare_results.get(key)
        ltr_matches = ltr_results.get(key)
        if base_matches is None or len(base_matches) == 0:
            od.write("\t\tNo base matches\n")
        if ltr_matches is None or len(ltr_matches) == 0:
            od.write("\t\tNo LTR matches\n")
        # print any disagreements
        base_sku_set = set(base_matches.items())
        ltr_sku_set = set(ltr_matches.items())
        sku_rank_diff = base_sku_set.difference(ltr_sku_set)
        if len(sku_rank_diff) > 0:
            od.write("\t\tResults diff (sku, rank): %s\n" % sku_rank_diff)


# Result is a dict with the keys being the skus that have clicks in the original click model and the value is the position in the
# ranking
def __judge_hits(all_skus_for_query, index, key, no_results, opensearch, query_object, query_type, results, seen):
    try:
        response = opensearch.search(body=query_object, index=index)
    except Exception as re:
        print(re, query_object)
    else:
        if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
            hits = response['hits']['hits']
            # Evaluate how many SKUs are in the top X results
            limit = len(hits)
            for i in range(limit):
                hit = hits[i]
                sku = int(hit['_source']['sku'][0])
                results["query"].append(key)
                results["type"].append(query_type)
                results["new"].append(seen)
                results["sku"].append(sku)
                results["rank"].append(i+1)
                results["score"].append(hit["_score"])
                if all_skus_for_query[all_skus_for_query == sku].count() > 0:
                    results["found"].append(True)
                else:
                    results["found"].append(False)

        else:
            #print("No results for query: %s" % query_object)
            no_results.append(key)

# Precision is the number of relevant (in our case clicked) out of the number of retrieved
def calculate_precision(results, type, num_queries_no_results, precision=10):
    num_q_total = len(results["query"].unique()) + num_queries_no_results
    typed_results = results[(results["type"] == type) & (results["found"] == True) & (results["rank"] < precision)]
    counts = typed_results.groupby("query")["rank"].count()
    precisions = counts/precision
    return precisions.sum() / num_q_total #average


def calculate_mrr(results, type, num_queries_no_results):
    num_q_total = len(results["query"].unique()) + num_queries_no_results
    typed_results = results[(results["type"] == type) & (results["found"] == True)]
    gb = typed_results.groupby(["query"])
    min_ranks = gb['rank'].min()
    r_ranks = 1 / min_ranks
    return r_ranks.sum() / num_q_total


def analyze_results(results_df, no_results_df, new_queries_df, opensearch, index, ltr_model_name, ltr_store_name, train_df, test_df, output_dir, precision=10, analyze_explains=False, max_explains=100):
    print("Queries not seen during training: [%s]\n%s\n\n" % (len(new_queries_df), new_queries_df))
    # MRR: mean reciprocal rank, closer to 1 is better, closer to zero is worse

    print("Simple MRR is %.3f" % (calculate_mrr(results_df, "simple", len(no_results_df["simple"]))))
    print("LTR Simple MRR is %.3f" % (calculate_mrr(results_df, "ltr_simple", len(no_results_df["ltr_simple"]))))
    print("Hand tuned MRR is %.3f" % (calculate_mrr(results_df, "hand_tuned", len(no_results_df["hand_tuned"]))))
    print("LTR Hand Tuned MRR is %.3f" % (calculate_mrr(results_df, "ltr_hand_tuned", len(no_results_df["ltr_hand_tuned"]))))
    # Caveat emmptor: precision is hard to define here, we're inferring a prior click as meaning the result is relevant.
    # This is self-serving, but really this whole thing is just trying to learn clicks
    print("")
    print("Simple p@%s is %.3f" % (precision, calculate_precision(results_df, "simple", len(no_results_df["simple"]), precision)))
    print("LTR simple p@%s is %.3f" % (precision, calculate_precision(results_df, "ltr_simple", len(no_results_df["ltr_simple"]), precision)))
    print("Hand tuned p@%s is %.3f" % (precision, calculate_precision(results_df, "hand_tuned", len(no_results_df["hand_tuned"]), precision)))
    print("LTR hand tuned p@%s is %.3f" % (precision, calculate_precision(results_df, "ltr_hand_tuned", len(no_results_df["ltr_hand_tuned"]), precision)))
    # Do some comparisons between the sets
    simple_df = results_df[results_df["type"] == "simple"]
    ltr_simple_df = results_df[results_df["type"] == "ltr_simple"]
    hand_tuned_df = results_df[results_df["type"] == "hand_tuned"]
    ltr_hand_tuned_df = results_df[results_df["type"] == "ltr_hand_tuned"]
    # Do some merging so we can compare
    simple_join = pd.merge(simple_df, ltr_simple_df, on=["query", "sku"], suffixes=("_simple", "_ltr"))
    simple_better = simple_join[(simple_join["rank_simple"] < simple_join["rank_ltr"]) & (simple_join["found_simple"] == True)]
    ltr_simple_better = simple_join[(simple_join["rank_simple"] > simple_join["rank_ltr"]) & ((simple_join["found_simple"] == True) | (simple_join["found_ltr"] == True))]
    simple_ltr_equal = simple_join[(simple_join["rank_simple"] == simple_join["rank_ltr"]) & (simple_join["found_simple"] == True)]
    print("Simple better: %s\tLTR_Simple Better: %s\tEqual: %s" % (len(simple_better), len(ltr_simple_better), len(simple_ltr_equal)))
    ht_join = pd.merge(hand_tuned_df, ltr_hand_tuned_df, on=["query", "sku"], suffixes=("_ht", "_ltr"))
    ht_better = ht_join[(ht_join["rank_ht"] < ht_join["rank_ltr"]) & (ht_join["found_ht"] == True)]
    ltr_ht_better = ht_join[(ht_join["rank_ht"] > ht_join["rank_ltr"]) & ((ht_join["found_ht"] == True) | (ht_join["found_ltr"] == True))]
    ht_ltr_equal = ht_join[(ht_join["rank_ht"] == ht_join["rank_ltr"]) & (ht_join["found_ht"] == True)]
    print("HT better: %s\tLTR_HT Better: %s\tEqual: %s" % (len(ht_better), len(ltr_ht_better), len(ht_ltr_equal)))
    print("Saving Better/Equal analysis to %s/analysis" % output_dir)
    analysis_output_dir = "%s/analysis" % output_dir
    if os.path.isdir(analysis_output_dir) == False:
        os.mkdir(analysis_output_dir)
    # OUtput our analysis
    simple_better.to_csv("%s/simple_better.csv" % analysis_output_dir, index=False)
    ltr_simple_better.to_csv("%s/ltr_simple_better.csv" % analysis_output_dir, index=False)
    simple_ltr_equal.to_csv("%s/simple_ltr_equal.csv" % analysis_output_dir, index=False)
    ht_better.to_csv("%s/ht_better.csv" % analysis_output_dir, index=False)
    ltr_ht_better.to_csv("%s/ltr_ht_better.csv" % analysis_output_dir, index=False)
    ht_ltr_equal.to_csv("%s/ht_ltr_equal.csv" % analysis_output_dir, index=False)
    # Output some subsamples where we did better on LTR AND the rank is in the top 20
    ltr_simple_top_20 = ltr_simple_better[ltr_simple_better["rank_ltr"] < 20]
    ltr_simple_top_20.to_csv("%s/simple_ltr_better_r20.csv" % analysis_output_dir, index=False)
    ltr_ht_top_20 = ltr_ht_better[ltr_ht_better["rank_ltr"] < 20]
    ltr_ht_top_20.to_csv("%s/ht_ltr_better_r20.csv" % analysis_output_dir, index=False)
    if analyze_explains:
        train_gb = train_df.groupby("query")
        print("Comparing simple vs LTR explains")
        simple_ltr_explains = compare_explains(simple_better, "ltr_simple", opensearch, index, ltr_model_name, ltr_store_name, train_gb, max_explains)
        simple_ltr_explains.to_csv("%s/analysis/simple_ltr_explains.csv" % output_dir, index=False)
        print("Comparing hand tuned vs LTR explains")
        ht_ltr_explains = compare_explains(ht_better, "ltr_hand_tuned", opensearch, index, ltr_model_name, ltr_store_name, train_gb, max_explains)
        ht_ltr_explains.to_csv("%s/analysis/hand_tuned_ltr_explains.csv" % output_dir, index=False)


# loop through, run the explain and extract the scores
# The dataframe is a joined one
def compare_explains(join, type, opensearch, index, ltr_model_name, ltr_store_name, train_gb, max_explains=100):

    query = []
    sku = []
    scores = [] # the top level score
    results = {"query": query, "sku":sku, "score": scores}
    ctr = 0
    for item in join.itertuples():
        ctr += 1
        if ctr % 10 == 0:
            print("Progress[%s]: %s" % (ctr, item.query))
        if max_explains == ctr:
            break
        click_prior_query = ""
        try:
            prior_clicks_for_query = train_gb.get_group(item.query)
            if prior_clicks_for_query is not None and len(prior_clicks_for_query) > 0:
                prior_doc_ids = prior_clicks_for_query.sku.drop_duplicates()
                prior_doc_id_weights = prior_clicks_for_query.sku.value_counts() # histogram gives us the click counts for all the doc_ids
                query_times_seen = prior_clicks_for_query.sku.count()
                click_prior_query = qu.create_prior_queries(prior_doc_ids, prior_doc_id_weights, query_times_seen)
        except KeyError as ke:
            pass #just means we can't find this query in the priors, which is OK

        query_obj, num_shoulds = get_explain_query_for_type(item.query, type, click_prior_query, ltr_model_name, ltr_store_name)
        if click_prior_query is None or click_prior_query == '':
            num_shoulds += 1 # if click prior is empty, then num shoulds will always be one less than a query with a valid click prior, which will throw off our parallel arrays
        #print("Explain query %s" % query_obj)
        response = opensearch.explain(index, item.sku, body=query_obj)
        # get the top level scores by description
        if response:
            details = response['explanation']['details']
            query.append(item.query)
            sku.append(item.sku)
            scores.append(response["explanation"]["value"])
            for idx, val in enumerate(details):
                feat_name = "clause_%s" % idx
                arry = results.get(feat_name, None)
                if arry is None:
                    arry = []
                    results[feat_name] = arry
                #clauses.append()
                #values.append("%s" % (val["value"]))
                arry.append(val["value"])
                if val["description"].find("LtrModel:") >= 0:
                    ltr_details = val["details"]
                    for ltr_detail in ltr_details:
                        #'description': 'Feature 2(manufacturer_match): [no match, default value 0.0 used]',
                        feat_name = ltr_detail["description"].split(":")[0]
                        arry = results.get(feat_name, None)
                        if arry is None:
                            arry = []
                            results[feat_name] = arry
                        arry.append(ltr_detail["value"])
            if (num_shoulds > len(details)): # this means not all clauses had explanations
                for i in range(len(details), num_shoulds):
                    feat_name = "clause_%s" % i
                    arry = results.get(feat_name, None)
                    if arry is None:
                        arry = []
                        results[feat_name] = arry
                    arry.append(0)
        else:
            print("No response for q: %s & sku: %s" % (item.query, item.sku))
    results_df = pd.DataFrame(results)
    return results_df

def get_feat_names(details):
    feat_names = set()
    for idx, val in enumerate(details):
        if val["description"].find("LtrModel:") >= 0:
            ltr_details = val["details"]
            for ltr_detail in ltr_details:
                #'description': 'Feature 2(manufacturer_match): [no match, default value 0.0 used]',
                feat_names.add(ltr_detail["description"].split(":")[0])
        break
    return feat_names

def get_explain_query_for_type(query, type, click_prior_query, ltr_model_name, ltr_store_name):
    num_shoulds = 0
    qo = None
    if type == "ltr_simple":
        qo = qu.create_simple_baseline(query, click_prior_query, None, include_aggs=False, highlight=False)
        qo, num_shoulds = lu.create_sltr_simple_query(query, qo, click_prior_query, ltr_model_name, ltr_store_name)
    elif type == "ltr_hand_tuned":
        qo = qu.create_query(query, click_prior_query, None, include_aggs=False, highlight=False)
        qo, num_shoulds = lu.create_sltr_hand_tuned_query(query, qo, click_prior_query, ltr_model_name, ltr_store_name)
    try:
        qo.pop("size")
    except:
        pass
    try:
        qo.pop("sort")
    except:
        pass
    try:
        qo.pop("_source")
    except:
        pass
    return qo, num_shoulds


def lookup_product(sku, opensearch, index="bbuy_products", source=None):
    try:
        return opensearch.get(index, sku, _source=source)
    except NotFoundError:
        return None


def lookup_query(query, all_clicks_df, opensearch, explain=False, index="bbuy_products", source=None):
    gb = all_clicks_df.groupby("query")
    if gb is not None:
        click_group = gb.get_group(query)
        if len(click_group) > 0:
            print("Query: %s has %s clicked docs" % (query, len(click_group)))
            for item in click_group.itertuples():
                sku = item.sku
                try:
                    doc = lookup_product(sku, opensearch, index=index, source=source)
                except NotFoundError as ne:
                    print("Couldn't find doc: %s" % sku)
                else:
                    print(json.dumps(doc, indent=4))
                    if explain:
                        query_obj = qu.create_query(query, None, include_aggs=False, highlight=False, source=source)
                        query_obj.pop("size")
                        query_obj.pop("sort")
                        query_obj.pop("_source")
                        print("Explain query %s" % query_obj)
                        response = opensearch.explain(index, sku, body=query_obj)
                        print(json.dumps(response, indent=4))
                    
                
        else:
            print("No clicks for query %s" % query)