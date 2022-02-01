# Some handy utilities for dealing with searches

import json

import query_utils as qu
from opensearchpy import NotFoundError


# Given a Test DataFrame, run the queries against the OpenSearch


def evaluate_test_set(test_data, all_clicks_df, opensearch, xgb_model_name, ltr_store, index, size=100, rescore_size=100, precision=10, output_diffs="diffs_output.json"):
    # (ranks_df, features_df) = data_prepper.get_judgments(test_data, True) # judgments as a Pandas DataFrame
    if precision > size:
        print("Precision can't be greater than the fetch size, changing the precision to be same as size")
        precision = size
    query_gb = test_data.groupby("query") #small
    query_all_gb = all_clicks_df.groupby(["query"]) #large
    source = ["sku", "name"]
    ltr_results = {}
    baseline_results = {}
    hand_tuned_results = {}
    results = {"baseline": baseline_results, "ltr": ltr_results, "hand_tuned": hand_tuned_results}
    no_base = set()
    no_ltr = set()
    no_hand_tuned = set()
    no_results = {"baseline": no_base, "ltr": no_ltr, "hand_tuned": no_hand_tuned}
    print("Running test queries")
    for key in query_gb.groups.keys():
        all_clicks_for_query = query_all_gb.get_group(key) # this is the set of docs in our sample that have clicks
        all_skus_for_query = all_clicks_for_query.sku.drop_duplicates()
        #print(key)
        # Score the baseline
        #print("\tRunning baseline:")
        query_object = qu.create_simple_baseline(key, filters=None, size=size, highlight=False, include_aggs=False, source=source)
        # don't care about no results here
        (baseline_results[key], missed) = __judge_hits(all_skus_for_query, index, key, no_base, opensearch, precision, query_object)
        # Run hand-tuned
        query_object = qu.create_query(key, filters=None, size=size, highlight=False, include_aggs=False, source=source)

        (hand_tuned_results[key], missed) = __judge_hits(all_skus_for_query, index, key, no_hand_tuned, opensearch, precision, query_object)
        #print(len(baseline_results[key]))
        # Score with LTR
        #print("\tRunning LTR:")
        query_object = qu.create_rescore_ltr_query(key, xgb_model_name, ltr_store, size=size, rescore_size=rescore_size, highlight=False, include_aggs=False, source=source)
        (ltr_results[key], missed) = __judge_hits(all_skus_for_query, index, key, no_ltr, opensearch, precision, query_object)
        all_skus_as_set = set(all_skus_for_query)
        found_keys = set(ltr_results[key].keys())
        #print("LTR[%s]: Retrieved, not in clicked: %s\nIn clicked: %s\nSet Diff: %s\n" % (key, missed, found_keys, all_skus_as_set.difference(found_keys)))
        #print(len(ltr_results[key]))
        # do some comparisons


    print("Zero results queries: %s" % no_results)
    # Do some analysis on the results
    print("Results analysis:")
    base_set = set(baseline_results.keys())
    ltr_set = set(ltr_results.keys())
    hand_set = set(hand_tuned_results.keys())
    with (open(output_diffs, 'w')) as od:
        od.write("Writing out diffs between baseline and LTR:\n")
        write_diffs(base_set, baseline_results, ltr_results, ltr_set, od)
        od.write("Writing out diffs between hand tuned and LTR:\n")
        write_diffs(hand_set, hand_tuned_results, ltr_results, ltr_set, od)

    print("Baseline MRR is %.3f" % (__calculate_mrr(baseline_results)))
    print("Hand tuned MRR is %.3f" % (__calculate_mrr(hand_tuned_results)))
    print("LTR MRR is %.3f" % (__calculate_mrr(ltr_results)))
    # Caveat emmptor: precision is hard to define here, we're inferring a prior click as meaning the result is relevant.
    # This is self-serving, but really this whole thing is just trying to learn clicks
    print("Baseline p@%s is %.3f" % (precision, __calculate_precision(baseline_results, precision)))
    print("Hand tuned p@%s is %.3f" % (precision, __calculate_precision(hand_tuned_results, precision)))
    print("LTR p@%s is %.3f" % (precision,__calculate_precision(ltr_results, precision)))
    return (results, no_results)


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
def __judge_hits(all_skus_for_query, index, key, no_results, opensearch, precision, query_object):
    results = {}
    missed = []
    try:
        response = opensearch.search(body=query_object, index=index)
    except Exception as re:
        print(re, query_object)
    else:
        if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
            hits = response['hits']['hits']
            # Evaluate how many SKUs are in the top X results
            limit = min(len(hits), precision)

            for i in range(limit):
                hit = hits[i]
                sku = int(hit['_source']['sku'][0])
                if all_skus_for_query[all_skus_for_query == sku].count() > 0:
                    name = hit['_source']['name']
                    #print("hit for %s  [sku: %s (id: %s)] at rank %s" % (name, sku, hit['_id'], i))
                    results[sku] = i
                else:
                    missed.append(sku)
            # capture what was missed


        else:
            #print("No results for query: %s" % query_object)
            no_results.add(key)
    return (results, missed)

# Precision is the number of relevant out of the number of retrieved
# Results has an entry if there was a match.  Value is the rank
def __calculate_precision(results, num_retrieved=10):
    if len(results) == 0:
        return 0
    prec = 0  # mean average precision
    #print(type(results))
    for res in results:
        prec += (len(results[res])/num_retrieved)
    return prec / len(results) #average


def __calculate_mrr(results):
    if len(results) == 0:
        return 0
    mrr = 0
    for item in results:
        matches = results[item]
        if matches is not None and len(matches) > 0:
            match_list = list(matches.values())
            match_list.sort()
            low_rank = match_list[0] + 1
            mrr += 1 / low_rank
    return mrr / len(results)



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