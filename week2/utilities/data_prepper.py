# This file processes our queries, runs them through OpenSearch against the BBuy Products index to fetch their "rank" and so they can be used properly in a click model

import ltr_utils as lu
import numpy
import pandas as pd
import query_utils as qu
from opensearchpy import RequestError
import numpy as np

# from importlib import reload

# %load week2_finished/utilities/query_utils.py
# %load -r 11-87 week2_finished/utilities/data_prepper.py
# In the real world, you'd probably use Spark or something, but we'll go with Pandas here
class DataPrepper:
    opensearch = None
    index_name = "bbuy_products"
    ltr_store_name = "week2"
    feature_names = []

    def __init__(self, opensearch_client, featureset_name="bbuy_product_featureset", index_name="bbuy_products",
                 ltr_store_name="week2", feature_names=None) -> None:
        self.opensearch = opensearch_client
        self.featureset_name = featureset_name
        self.index_name = index_name
        self.ltr_store_name = ltr_store_name
        if feature_names is not None:
            self.feature_names = feature_names

    def __get_query_id(self, query, query_ids_map, query_counter):
        qid = query_ids_map.get(query, None)
        if not qid:
            query_counter += 1
            qid = query_counter
            query_ids_map[query] = qid
        return qid, query_counter

    # Use the set of clicks and assume the clicks are in proportion to the actual rankings due to position bias
    #
    ## CAVEAT EMPTOR: WE ARE BUILDING A SYNTHETIC IMPRESSIONS DATA SET BECAUSE WE DON'T HAVE A PROPER ONE.
    #
    #
    def synthesize_impressions(self, clicks_df, min_impressions=20, min_clicks=10):
        pairs = clicks_df.groupby(['query', 'sku']).size().reset_index(name='clicks')
        pairs['rank'] = pairs.groupby('query')['clicks'].rank('dense', ascending=False)
        pairs['num_impressions'] = pairs.groupby('query')['clicks'].transform('sum')
        # cut off the extreme end of the long tail due to low confidence in the evidence
        print(
            "IMPLEMENT ME: cut off the extreme end of the long tail due to low confidence in the evidence by min clicks and min impressions")

        pairs['doc_id'] = pairs['sku']  # not technically the doc id, but since we aren't doing a search...
        pairs['product_name'] = "fake"
        query_ids = []
        query_ids_map = {}
        query_counter = 1
        for item in pairs.itertuples():
            query_id, query_counter = self.__get_query_id(item.query, query_ids_map, query_counter)
            query_ids.append(query_id)

        pairs["query_id"] = query_ids
        return (pairs, query_ids_map)

    #########
    ##
    ## CAVEAT EMPTOR: WE ARE BUILDING A SYNTHETIC IMPRESSIONS DATA SET BECAUSE WE DON'T HAVE A PROPER ONE.
    ## YOU WOULD NOT DO THIS IN THE REAL WORLD, BUT YOU WOULD DO SOMETHING SIMILAR BY LOGGING YOUR IMPRESSIONS, BOTH POSITIVE AND NEGATIVE
    ##
    #########
    # For each query, send it to OpenSearch and log all the documents we retrieved and their position
    # Return the impressions data as a Pandas Data Frame
    def generate_impressions(self, query_df, all_clicks_df, query_ids_map, retrieval_size=50, min_impressions=20,
                             min_clicks=10):
        # Capture judgments info into a dict of arrays so we can convert it to a Data Frame
        query_counter = 1
        query_ids_list = []

        query_strs = []
        doc_ids = []
        ranks = []
        clicks = []
        num_impressions = []
        product_names = []
        skus = []
        query_gb = query_df.groupby("query")  # small
        query_all_gb = all_clicks_df.groupby(["query"])  # large
        no_results = set()
        total_query_count = all_clicks_df.count()
        for key in query_gb.groups.keys():
            query_id, query_counter = self.__get_query_id(key, query_ids_map, query_counter)
            print("Q[%s]: %s" % (query_id, key))
            query_times_seen = all_clicks_df[all_clicks_df["query"] == key]["query"].count()
            query_obj = qu.create_query(key, filters=None, size=retrieval_size, include_aggs=False, highlight=False,
                                        source=["name", "sku"])  # TODO: handle categories
            # Fetch way more than usual so we are likely to see our documents that have been clicked
            try:
                response = self.opensearch.search(body=query_obj, index=self.index_name)
            except RequestError as re:
                print(re, query_obj)
            else:
                if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
                    # we have a response with some hits
                    hits = response['hits']['hits']
                    # print(hits)
                    all_clicks_for_query = query_all_gb.get_group(
                        key)  # this is the set of docs in our sample that have clicks
                    all_skus_for_query = all_clicks_for_query.sku  # we are comparing skus later, so grab the Series now

                    total_clicked_docs_per_query = 0
                    for (idx, hit) in enumerate(hits):
                        query_ids_list.append(query_id)
                        query_strs.append(key)
                        doc_ids.append(hit['_id'])
                        ranks.append(idx)
                        sku = int(hit['_source']['sku'][0])
                        skus.append(sku)
                        num_clicks = self.__num_clicks(all_skus_for_query, sku)
                        if num_clicks > 0:
                            total_clicked_docs_per_query += 1
                        num_impressions.append(query_times_seen)
                        clicks.append(num_clicks)
                        if hit['_source'].get('name') is not None:
                            product_names.append(hit['_source']['name'][0])
                        else:
                            product_names.append("SKU: %s -- No Name" % sku)
                        # print("Name: {}\n\nDesc: {}\n".format(hit['_source']['name'], hit['_source']['shortDescription']))

                    print("\tQ[%s]: %s clicked" % (query_id, total_clicked_docs_per_query))
                else:
                    if response and (response['hits']['hits'] == None or len(response['hits']['hits']) == 0):
                        print("No results for query: %s" % key)
                        no_results.add(key)
                    else:
                        print(response)
                        print("Invalid response for query %s" % query_obj)
        print("Zero results queries: %s" % no_results)
        impressions_df = pd.DataFrame({
            "query_id": query_ids_list,
            "query": query_strs,
            "doc_id": doc_ids,
            "rank": ranks,
            "clicks": clicks,
            "sku": skus,
            "num_impressions": num_impressions,
            "product_name": product_names
        })
        # remove low click/impressions,
        print(
            "IMPLEMENT ME: cut off the extreme end of the long tail due to low confidence in the evidence by min clicks and min impressions")

        return impressions_df, query_ids_map

    def log_features(self, train_data_df, terms_field="_id"):
        feature_frames = []
        query_gb = train_data_df.groupby("query")
        no_results = {}
        for key in query_gb.groups.keys():
            # get all the docs ids for this query
            group = query_gb.get_group(key)
            doc_ids = group.doc_id.values
            if isinstance(doc_ids, numpy.ndarray):
                doc_ids = doc_ids.tolist()
            ltr_feats_df = self.__log_ltr_query_features(group[:1]["query_id"], key, doc_ids, no_results,
                                                         terms_field=terms_field)
            if ltr_feats_df is not None:
                feature_frames.append(ltr_feats_df)

        features_df = None
        if len(feature_frames) > 0:
            features_df = pd.concat(feature_frames)
        print("The following queries produced no results: %s" % no_results)
        return features_df

    # Features look like:
    # {'log_entry': [{'name': 'title_match',
    #          'value': 7.221403},
    #         {'name': 'shortDescription_match'},
    #         {'name': 'longDescription_match'},
    #         {'name': 'onsale_function', 'value': 0.0},
    #         {'name': 'short_term_rank_function', 'value': 1922.0},
    #         {'name': 'medium_term_rank_function', 'value': 7831.0},
    #         {'name': 'long_term_rank_function', 'value': 4431.0},
    #         {'name': 'sale_price_function', 'value': 949.99},
    #         {'name': 'price_function', 'value': 0.0}]}]
    # For each query, make a request to OpenSearch with SLTR logging on and extract the features
    def __log_ltr_query_features(self, query_id, key, query_doc_ids, no_results, terms_field="_id"):

        log_query = lu.create_feature_log_query(key, query_doc_ids, self.featureset_name,
                                                self.ltr_store_name,
                                                size=len(query_doc_ids), terms_field=terms_field)
        if log_query is not None:
            try:
                response = self.opensearch.search(body=log_query, index=self.index_name)
            except RequestError as re:
                print("Error logging features", re, log_query)
            else:
                # Get the features that have been logged.  They aren't in the same order as our first round, so we need to line them up
                if response and response['hits']['hits'] and len(response['hits']['hits']) > 0:
                    hits = response['hits']['hits']
                    # extract the feautres based on the features passed into the Prepper
                    feature_results = {}  # key is the name of the feature from self.feature_names, value is an array of values
                    # for feature in self.feature_names: #initialize storage
                    feature_results["doc_id"] = []  # capture the doc id so we can join later
                    feature_results["query_id"] = []  # ^^^
                    feature_results["sku"] = []  # ^^^
                    for (idx, hit) in enumerate(hits):
                        features = hit['fields']['_ltrlog'][0]['log_entry']
                        feature_results["doc_id"].append(int(hit['_id']))
                        feature_results["sku"].append(int(hit['_source']['sku'][0]))
                        # super redundant, but it will make it easier to join later
                        feature_results["query_id"].append(int(query_id))
                        print("IMPLEMENT ME")
                        # IMPLEMENT: for each feature in `features` logged by SLTR, add it to a parallel array of feature_results
                        # such that there is an entry in feature_results for that feature and the value is an array of all the feature values
                        # e.g.  `feature_results[feat_name] = [.....]
                        # for feat_idx, feature in enumerate(features):
                    frame = pd.DataFrame(feature_results)
                    # Make sure we type things appropriately
                    return frame.astype({'doc_id': 'int64', 'query_id': 'int64', 'sku': 'int64'})
                else:  # Save any queries we couldn't match so that we can debug them later
                    no_results[key] = query_doc_ids
        else:
            # REMOVE_START -- REMOVE FROM HERE DOWN TO THE 'REMOVE_END' MARKER AND REPLACE WITH A PROPER HANDLING OF NO LOG QUERY
            print("!!!Hey, have you implemented create_feature_log_query?  If so, you really shouldn't be here!!!!. REMOVE THIS BLOCK")
            feature_results = {}
            feature_results["doc_id"] = []  # capture the doc id so we can join later
            feature_results["query_id"] = []  # ^^^
            feature_results["sku"] = []
            feature_results["fake_feature_1"] = []
            feature_results["fake_feature_2"] = []
            rng = np.random.default_rng(12345)
            for doc_id in query_doc_ids:
                feature_results["doc_id"].append(doc_id)  # capture the doc id so we can join later
                feature_results["query_id"].append(query_id)
                feature_results["sku"].append(doc_id)  # ^^^
                feature_results["fake_feature_1"].append(rng.random())
                feature_results["fake_feature_2"].append(rng.random())
            print("REMOVE ^^^^ up to the other print statement once you've implemented proper query logging")
            frame = pd.DataFrame(feature_results)
            return frame.astype({'doc_id': 'int64', 'query_id': 'int64', 'sku': 'int64'})
            # REMOVE_END -- REMOVE FROM HERE UP TO THE 'REMOVE_START' COMMENT ABOVE
        return None

    # Can try out normalizing data, but for XGb, you really don't have to since it is just finding splits
    def normalize_data(self, ranks_features_df, feature_set, normalize_type_map):
        # we need to get some stats from OpenSearch and then use that to normalize our data
        agg_fields = []
        aggs = {}
        for feature in feature_set['featureset']['features']:
            func_temp = feature['template'].get("function_score")
            if func_temp is not None:
                # get the field
                funcs = func_temp.get("functions",
                                      [func_temp.get("field_value_factor")])  # could also be a field_value_factor alone
                for func in funcs:
                    agg_fields.append(func['field_value_factor']['field'])
        stats_query = qu.create_stats_query(agg_fields)
        try:
            response = self.opensearch.search(stats_query, self.index_name)
        except RequestError as re:
            print("Unable to get aggs: %s\t%s" % (stats_query, re))
            raise re
        else:
            # we now have an OpenSearch response with a bunch of stats info.  We mainly care about min/max/avg/std.dev
            if response and response['aggregations'] and len(response['aggregations']) > 0:
                aggs = response['aggregations']

                # Initialize with the identify function for every
                for agg in agg_fields:
                    stats = aggs[agg]
                    # print("agg: %s: %s" %(agg, stats))
                    norm_type = normalize_type_map.get(agg, "default")
                    # We only support these two since they are the two main normalizers in the LTR plugin
                    if norm_type == "min-max":
                        min = stats["min"]
                        max = stats["max"]
                        max_min = max - min
                        ranks_features_df["%s_norm" % agg] = ranks_features_df[agg].apply(lambda x: (x - min) / max_min)
                    elif norm_type == "std-dev":
                        avg = stats["avg"]
                        std_dev = stats["std_deviation"]
                        ranks_features_df["%s_norm" % agg] = ranks_features_df[agg].apply(lambda x: (x - avg) / std_dev)
                    # else:
                    # Do nothing for now
            else:
                print("No aggregations found in %s" % response)
        return (ranks_features_df,
                aggs)  # return out the aggregations, bc we are going to need it to write the model normalizers

    # Determine the number of clicks for this sku given a query (represented by the click group)
    def __num_clicks(self, all_skus_for_query, test_sku):
        print("IMPLEMENT NUM_CLICKS")
        return 0
