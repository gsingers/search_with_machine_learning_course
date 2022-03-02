####
#
#  Our main class for creating an LTR model via XG Boost and uploading it to OpenSearch
#
###

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import argparse
import json
import os
from getpass import getpass
from urllib.parse import urljoin

import click_models as cm
import data_prepper as dp
import ltr_utils as ltr
import pandas as pd
import search_utils as su
import xgb_utils as xgbu
from opensearchpy import OpenSearch




if __name__ == "__main__":
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
    parser = argparse.ArgumentParser(description='Build LTR.')
    # TODO: setup argparse requirements/dependencies to better enforce arguments that require other arguments
    general = parser.add_argument_group("general")
    general.add_argument("-i", '--index', default="bbuy_products",
                         help='The name of the main index to search')
    general.add_argument("-s", '--host', default="localhost",
                         help='The OpenSearch host name')
    general.add_argument("-p", '--port', type=int, default=9200,
                         help='The OpenSearch port')
    general.add_argument('--user',
                         help='The OpenSearch admin.  If this is set, the program will prompt for password too. If not set, use default of admin/admin')
    general.add_argument("-l", '--ltr_store', default="week2",
                         help='The name of the LTR store.  Will be prepended with _ltr on creation')
    general.add_argument("-a", '--all_clicks',
                         help='The path to the CSV file containing all click/session data.  This is required if doing --generate_impressions or --xgb_test')
    general.add_argument("--output_dir", default="output", help="the directory to output all files to")

    dp_group = parser.add_argument_group("LTR Data Prep")
    dp_group.add_argument("--ltr_terms_field", default="_id",
                          help="If --synthesize our data, this should be set to 'sku'")
    dp_group.add_argument('--normalize_json',
                          help='A path to a JSON map of LTR feature-normalizer type pairs. If unset, data normalization will not happen.  See week2/conf/normalize_types.json for an example')

    dp_group.add_argument('--synthesize', action="store_true",
                          help='if set, along with --generate_impressions, creates impressions based on an implied ranking in the click logs.  Writes to --impressions_file.')
    dp_group.add_argument('--generate_impressions', action="store_true",
                          help='Generate impressions by running a search and comparing results using the --train_file file.  Writes to --impressions_file. See also --synthesize.')
    dp_group.add_argument('--generate_num_rows', default=5000, type=int,
                          help='The number of impressions to generate using retrieval.  Randomly samples from all_clicks.  Use with --generate_impressions.  Ignored if --synthesize')
    dp_group.add_argument('--min_impressions', default=20, type=int,
                          help='The minimum number of times a query must be seen to be included in the impressions set')
    dp_group.add_argument('--min_clicks', default=10, type=int,
                          help='The minimum number of clicks a doc must have to be included in the impressions set')
    dp_group.add_argument('--query_ids', default="query_to_query_ids.json",
                          help='The name of the file to read/write under the --output_dir as JSON')
    dp_group.add_argument("-r", '--impressions_file', default="impressions.csv",
                          help='Where to write the ranks/features CSV file to under --output_dir.  Output is written from a Pandas data frame')

    ltr_group = parser.add_argument_group("LTR Store Creation and Features")
    ltr_group.add_argument("-c", '--create_ltr_store', action="store_true",
                           help='Set the flag to create the LTR store.  If one exists, it will be deleted')
    ltr_group.add_argument("-f", '--featureset',
                           help='The path to the Featureset JSON file to read from')
    ltr_group.add_argument("-n", '--featureset_name', default="bbuy_main_featureset",
                           help='The name of the featureset')
    ltr_group.add_argument('--upload_featureset', action="store_true",
                           help='Upload the featureset given by the --featureset argument to OpenSearch')
    ltr_group.add_argument("-u", '--upload_ltr_model', action="store_true",
                           help='Upload XGB LTR model under the given featureset. Requires --featureset_name and --xgb_model')

    xgb_group = parser.add_argument_group("XGB Model Training and Testing")
    xgb_group.add_argument("-x", '--xgb',
                           help='Train an XGB Boost model using the training file given')
    xgb_group.add_argument("-t", '--create_xgb_training', action="store_true",
                           help='Create the training data set by logging the features for the training file and then outputting in RankSVM format.  Must have --train_file and --featureset')
    xgb_group.add_argument('--train_file', default="train.csv",
                           help='Where to load the training file from under the output_dir.  Required when using --create_xgb_training')
    xgb_group.add_argument('--xgb_conf', default="xgb-conf.json",
                           help='Path to XGB parameters JSON dictionary.  See week2/conf/xgb-conf.json')
    xgb_group.add_argument('--xgb_feat_map', default="xgb-feat-map.txt",
                           help='File name under --output_dir containing the feature map.  Must be set when creating training data.  See week2/conf/xgb-feat-map.txt')
    xgb_group.add_argument("--xgb_rounds", default=5, type=int, help="The number of rounds to train the model on.")
    xgb_group.add_argument("--xgb_model", default="xgb_model.model",
                           help="The file name to read/write the XGB model to in --output_dir. Two files will be written: 1 with the original XBG model and 1 that is ready for uploading to LTR (name with '.ltr' appended)")
    xgb_group.add_argument("--xgb_model_name", default="ltr_model", help="The name of the model")
    xgb_group.add_argument("--xgb_plot", action="store_true",
                           help="Writes model analysis images (.png) to the --output_dir. Requires the --xgb_model, --xgb_model_name and --xgb_feat_map args")
    xgb_group.add_argument("--xgb_test",
                           help="Given a path to a test data set, created separately from the train set, see how our model does!")
    xgb_group.add_argument("--xgb_test_output", default="xgb_test_output.csv",
                           help="File under --output_dir to write the differences between baseline and LTR search")
    xgb_group.add_argument("--xgb_test_num_queries", default=100, type=int,
                           help="Of the test data, only run this many queries when testing.")
    xgb_group.add_argument("--xgb_main_query_weight", default=1, type=float,
                           help="For the rescore query, how much weight to give the main query.")
    xgb_group.add_argument("--xgb_rescore_query_weight", default=2, type=float,
                           help="For the rescore query, how much weight to give the rescore query.")

    analyze_group = parser.add_argument_group("Analyze Test Results")
    analyze_group.add_argument("--analyze", action="store_true",
                               help="Calculate a variety of stats and other things about the results.  Uses --xgb_test_output")
    analyze_group.add_argument("--precision", type=int, default=10, help="What precision level to report")
    analyze_group.add_argument("--analyze_explains", action="store_true",
                               help="Run the queries from LTR queries that performed WORSE than the non-LTR query through explains and output the values.  Expensive.  Uses --xgb_test_output.  Outputs --output_dir as simple_ltr_explains.csv and ltr_hand_tuned_explains.csv.")
    analyze_group.add_argument("--max_explains", type=int, default=100, help="The maximum number of explains to output")

    click_group = parser.add_argument_group("Click Models")
    click_group.add_argument("--click_model", choices=["ctr", "binary", "heuristic"], default="ctr",
                             help='Simple Click-through-rate model')
    click_group.add_argument("--downsample", action="store_true",
                             help='Downsample whatever is most prevelant to create a more balanced training set.')

    split_group = parser.add_argument_group("Train/Test Splits")
    split_group.add_argument("--split_input",
                             help="If specified, will split the given file into training and testing, writing it to the file name given as an argument into --split_train and --split_test")
    split_group.add_argument("--split_train", default="train.csv",
                             help="The name of the training file to output under --output_dir")
    split_group.add_argument("--split_test", default="test.csv",
                             help="The name of the test file to output to under --output_dir")
    split_group.add_argument("--split_train_rows", type=int,
                             help="The total number of rows from the input file to put in the train split.  Limiting the rows can be helpful for testing code, but likely won't produce good models.")
    split_group.add_argument("--split_test_rows", type=int,
                             help="The total number of rows from the input file to put in the test split.  Helpful for testing code, but likely won't produce good results since it won't have insights into clicks.  See --xgb_test_num_queries.")

    # Some handy utilities
    util_group = parser.add_argument_group("Utilities")
    util_group.add_argument("--lookup_query",
                            help="Given a query in --all_clicks, dump out all the product info for items that got clicks")
    util_group.add_argument("--lookup_explain", action="store_true",
                            help="With --lookup_query, run explains for each query/sku pair")
    util_group.add_argument("--lookup_product", help="Given a SKU, return the product")
    util_group.add_argument("--verify_products", action="store_true",
                            help="Looks through all SKUs in --all_clicks and reports the ones that aren't in the index. Argument is where to output the items to under --output. WARNING: This is slow.")
    util_group.add_argument("--verify_file", default="validity.csv",
                            help="The filename to store --verify_products output to under the --output_dir.  If set with --all_clicks or --split_input and the file exists, then this file will be used to filter bad SKUs from click file")

    args = parser.parse_args()
    output_file = "output.txt"
    featureset_file = "featureset.json"
    if len(vars(args)) == 0:
        parser.print_usage()
        exit()

    host = args.host
    port = args.port
    if args.user:
        password = getpass()
        auth = (args.user, password)

    base_url = "https://{}:{}/".format(host, port)
    opensearch = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        # client_cert = client_cert_path,
        # client_key = client_key_path,
        use_ssl=True,
        verify_certs=False,  # set to true if you have certs
        ssl_assert_hostname=False,
        ssl_show_warn=False,

    )
    output_dir = args.output_dir
    if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

    ltr_store_name = args.ltr_store  # a little extra housekeeping due to the finickiness of the SLTR query
    ltr_store_path = "_ltr/" + args.ltr_store
    ltr_model_path = urljoin(base_url, ltr_store_path)
    feat_name = args.featureset_name
    index_name = args.index
    # Prep our data
    data_prepper = dp.DataPrepper(opensearch, feat_name, index_name, ltr_store_name)
    if args.split_input:
        # Split based on date.  All of our train data will be before a given date, and all test data will be after.
        # This simulates the real world and allows us to safely use prior clicks in our baseline retrieval and models
        data_prepper.create_splits(args.split_input, args.split_train, args.split_test, output_dir,
                                   args.split_train_rows, args.split_test_rows, args.verify_file)

    # Create the LTR Store
    if args.create_ltr_store:
        ltr.create_ltr_store(ltr_model_path, auth)

    all_clicks_df = None
    # Load up all of our data and filter it to get rid of junk data (promo codes, SKUs that don't exist
    if args.all_clicks:
        try:
            print("Loading all clicks from %s" % args.all_clicks)
            all_clicks_df = pd.read_csv(args.all_clicks, parse_dates=['click_time', 'query_time'])
            all_clicks_df = data_prepper.filter_junk_clicks(all_clicks_df, args.verify_file, output_dir)
            # all_clicks_df = all_clicks_df.astype({'click_time': 'datetime64', 'query_time':'datetime64'})
        except Exception as e:
            print("Error loading all clicks data")
            print(e)
            exit(2)

    # uplaod the LTR featureset
    if args.upload_featureset:
        featureset_path = urljoin(ltr_model_path + "/", "_featureset/{}".format(feat_name))
        print("Installing %s featureset at %s" % (args.featureset, featureset_path))
        with open(args.featureset) as json_file:
            the_feature_set = json.load(json_file)
            rsp = ltr.post_featureset(featureset_path, the_feature_set, auth)
            print("Featureset Creation: %s" % rsp)
    # Upload an LTR model
    if args.upload_ltr_model:
        # delete any old model first
        ltr.delete_model(urljoin(ltr_model_path + "/", "_model/{}".format(args.xgb_model_name)), auth)
        featureset_path = urljoin(ltr_model_path + "/", "_featureset/{}".format(feat_name))
        model_path = urljoin(featureset_path + "/", "_createmodel")
        os_model_file = "%s.ltr" % args.xgb_model
        with open(os_model_file) as model_file:
            ltr.upload_model(model_path, json.load(model_file), auth)


    ######
    #
    # Impressions are candidate queries with *simulated* ranks added to them as well as things like number of impressions
    # and click counts.  Impressions are what we use to then generate training data.  In the real world, you wouldn't
    # need to do this because you would be logging both clicked and unclicked events.
    # TLDR: we are trying to build a dataset that approximates what Best Buy search looked like back when this data was captured.
    # We have two approaches to impressions:
    # 1) We synthesize/infer them from the existing clicks, essentially assuming there is a built in position bias in the logs that *roughly* approximates the actual ranking of Best Buy search
    #    back when this data was captured.  Run using --generate_impressions and --synthesize
    # 2) Taking --generate_num_rows, run a random sample of queries through our current search engine.  If we find docs that have clicks, mark them as relevant.  All else are non-relevant.
    # Both approaches add rank, clicks and num_impressions onto the resulting data frame
    # We also dump out a map of queries to query ids.  Query ids are used in our XGB model.
    # Outputs to --output_dir using the --impressions_file argument, which defaults to impressions.csv
    ######
    if args.generate_impressions:
        impressions_df = None
        train_df = None
        if args.train_file:  # these should be pre-filtered, assuming we used our splitter, so let's not waste time filtering here
            train_df = pd.read_csv(args.train_file, parse_dates=['click_time', 'query_time'])
        else:
            print("You must provide the --train_file option")
            exit(2)

        if args.synthesize:
            (impressions_df, query_ids_map) = data_prepper.synthesize_impressions(train_df,
                                                                                  min_impressions=args.min_impressions,
                                                                                  min_clicks=args.min_clicks)
        else:
            # use the synthesize to feed into our generate
            (impressions_df, query_ids_map) = data_prepper.synthesize_impressions(train_df,
                                                                                  min_impressions=args.min_impressions,
                                                                                  min_clicks=args.min_clicks)
            impressions_df.drop(["product_name", "sku"], axis=1)
            impressions_df = impressions_df.sample(n=args.generate_num_rows).reset_index(drop=True)  # shuffle things
            # impressions_df = impressions_df[:args.generate_num_rows]
            (impressions_df, query_ids_map) = data_prepper.generate_impressions(impressions_df,
                                                                                query_ids_map,
                                                                                min_impressions=args.min_impressions,
                                                                                min_clicks=args.min_clicks)  # impressions as a Pandas DataFrame
        print("Writing impressions to file: %s/%s" % (output_dir, args.impressions_file))
        impressions_df.to_csv("%s/%s" % (output_dir, args.impressions_file), index=False)
        query_ids = query_ids_map
        # be sure to write out our query id map
        with open("%s/%s" % (output_dir, args.query_ids), 'w') as qids:
            qids.write(json.dumps(query_ids_map))

    #####
    #
    # Given an --impressions_file, create an SVMRank formatted output file containing one row per query-doc-features-comments.
    # Looping over impressions, this code issues queries to OpenSearch using the SLTR EXT function to extract LTR feaatures per every query-SKU pair
    # It then optionally normalizes the data (we will not use this in class, but it's there for future use where we don't use XGB, since XGB doesn't need normalization since it's calculating splits)
    # We also apply any click models we've implemented to then assign a grade/relevance score for each and every row.  See click_models.py.
    # Click models can also optionally downsample to create a more balanced training set.
    # Finally, we output two files: 1) training.xgb -- the file to feed to XGB for training
    # 2) training.xgb.csv -- a CSV version of the training data that is easier to work with in Pandas than the XGB file.
    #       This CSV file can be useful for debugging purposes.
    #
    #####
    if args.create_xgb_training and args.impressions_file:
        print("Loading impressions from %s/%s" % (output_dir, args.impressions_file))
        impressions_df = pd.read_csv("%s/%s" % (output_dir, args.impressions_file))

        if impressions_df is not None:
            # We need a map of normalize types for our features.  Would be nice if we could store this on the featureset
            normalize_type_map = {}
            if args.normalize_json:
                with open(args.normalize_json) as json_file:
                    types = json.load(json_file)
                    for item in types:
                        normalize_type_map[item['name']] = item['normalize_function']
            # We need our featureset
            with open(args.featureset) as json_file:
                the_feature_set = json.load(json_file)
                # Log our features for the training set
                print("Logging features")
                features_df = data_prepper.log_features(impressions_df, terms_field=args.ltr_terms_field)
                # Calculate some stats so we can normalize values.
                # Since LTR only supports min/max, mean/std. dev and sigmoid, we can only do that
                if args.normalize_json:
                    # Aggregations here returns the stats about our features, like min/max, std dev.  If we ever use
                    # https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/training-models.html#creating-a-model-with-feature-normalization
                    # we will need these to be saved/looked up so that we can add the normalizers to the model
                    (features_df, aggregations) = data_prepper.normalize_data(features_df, the_feature_set,
                                                                              normalize_type_map)
                    # Write out the normalized DF
                    features_df.to_csv("%s.normalized" % args.impressions_file)
                else:
                    aggregations = {}
                # Join the features data to the impressions data
                # drop the features_df doc_id, as it isn't needed anymore
                features_df.drop("doc_id", axis=1, inplace=True)
                features_df.to_csv("%s/features.csv" % output_dir)
                # Merge our impressions with our features using a left join on query_id and sku
                train_features_df = pd.merge(impressions_df, features_df, how="left", on=["query_id", "sku"])
                train_features_df["doc_id"] = train_features_df["sku"]
                # Apply any specified click model.
                train_features_df = cm.apply_click_model(train_features_df, args.click_model,
                                                         downsample=args.downsample)
                # Now write out in XGB/SVM Rank format
                print("NAN counts: %s" % train_features_df.isna().any().count())
                train_features_df = train_features_df.fillna(0)
                train_features_df = train_features_df.sample(frac=1)  # shuffle
                train_features_df.to_csv("%s/training.xgb.csv" % output_dir)
                ltr.write_training_file(train_features_df, "%s/training.xgb" % output_dir,
                                        "%s/%s" % (output_dir, args.xgb_feat_map))
        else:
            print("Unable to create training file, no ranks/features data available.")


    #############
    #
    # Train a model using XG Boost!  Taking in the training file (training.xgb by default) specified by --xgb,
    # build a model by iterating --xgb_rounds using the --xgb_conf (see https://xgboost.readthedocs.io/en/stable/python/python_intro.html#setting-parameters)
    # Once training is complete, dump out the model as JSON and in the OpenSearch LTR model format (which has weird escaping: https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/training-models.html)
    # Also save in XGB binary format.
    #
    #############
    if args.xgb:
        # Defaults

        bst, xgb_params = xgbu.train(args.xgb, args.xgb_rounds, args.xgb_conf)
        print("Dumping out model using feature map: %s" % args.xgb_feat_map)
        model = bst.get_dump(fmap=("%s/%s" % (output_dir, args.xgb_feat_map)), dump_format='json')
        # Write out both the raw and the LTR ready model to disk
        # Create our metadata for uploading the model
        model_name = args.xgb_model_name
        ltr.write_opensearch_ltr_model(model_name, model, "%s/%s" % (output_dir, args.xgb_model),
                                       objective=xgb_params.get("objective", "reg:logistic"))
        print("Saving XGB Binary model to %s/%s" % (output_dir, args.xgb_model))
        bst.save_model("%s/%s" % (output_dir, args.xgb_model))

    # Output some useful XGB Plots using matplotlib: https://xgboost.readthedocs.io/en/stable/python/python_api.html#module-xgboost.plotting
    if args.xgb_plot:
        xgbu.plots("%s/%s" % (output_dir, args.xgb_model), args.xgb_model_name,
                   "%s/%s" % (output_dir, args.xgb_feat_map), output_dir)

    ################
    #
    # Taking in the --xgb_test file and the --train_file (for accessing click priors), run --xgb_test_num_queries through
    # OpenSearch and retrieve the results.  Creates and writes several data frames to --output_dir:
    # 1) --xgb_test_output -- the main results, as CSV.  Contains info about where and what was retrieved.
    # 2) --xgb_test_output appended with .no_results -- All the queries that returned zero results
    # 3) --xgb_test_output appended with .new_queries -- All the queries that were "new" to us in the test set (e.g. we never saw this query in training).
    #         These can be useful for debugging and to see how well we generalize
    #
    ################
    if args.xgb_test:
        # To test, we're going to calculate MAP by looking at how many "relevant" documents were in the top X of
        # our result set.
        test_data = pd.read_csv(args.xgb_test, parse_dates=['click_time', 'query_time'])
        train_df = None
        # we use the training file for priors, but we must make sure we don't have leaks
        if args.train_file:  # these should be pre-filtered, assuming we used our splitter, so let's not waste time filtering here
            train_df = pd.read_csv(args.train_file, parse_dates=['click_time', 'query_time'])
        else:
            print("You must provide the --train_file option")
            exit(2)
        # DataFrame: query, doc, rank, type, miss, score, new
        results_df, no_results = su.evaluate_test_set(test_data, train_df, opensearch, args.xgb_model_name,
                                                      args.ltr_store, args.index, num_queries=args.xgb_test_num_queries,
                                                      main_query_weight=args.xgb_main_query_weight, rescore_query_weight=args.xgb_rescore_query_weight
                                                      )
        print("Writing results of test to %s" % "%s/%s" % (output_dir, args.xgb_test_output))
        results_df.to_csv("%s/%s" % (output_dir, args.xgb_test_output), index=False)
        no_results_df = pd.DataFrame(no_results)
        no_results_df.to_csv("%s/%s.no_results" % (output_dir, args.xgb_test_output), index=False)
        print("Meta:\nModel name: %s, Store Name: %s, Index: %s, Precision: %s \n" % (
        args.xgb_model_name, args.ltr_store, args.index, 10))
        # do some comparisons
        print("Zero results queries: %s\n\n" % no_results)
        new_queries_df = results_df[results_df["new"] == True]["query"].drop_duplicates()
        new_queries_df.to_csv("%s/%s.new_queries" % (output_dir, args.xgb_test_output), index=False)

    # Given the output of --xgb_test, output some useful info about things like MRR and Precision.  Also creates a number
    # of interesting join data frames that can be used to compare results.
    if args.analyze:
        pd.set_option('display.max_columns', None)
        test_df = pd.read_csv("%s/test.csv" % output_dir, parse_dates=['click_time', 'query_time'])
        train_df = pd.read_csv("%s/%s" % (output_dir, args.train_file), parse_dates=['click_time', 'query_time'])

        print("Analyzing results from %s/%s" % (output_dir, args.xgb_test_output))
        results_df = pd.read_csv("%s/%s" % (output_dir, args.xgb_test_output))
        no_results_df = pd.read_csv("%s/%s.no_results" % (output_dir, args.xgb_test_output))
        new_queries_df = pd.read_csv("%s/%s.new_queries" % (output_dir, args.xgb_test_output))
        su.analyze_results(results_df, no_results_df, new_queries_df, opensearch, args.index, args.xgb_model_name,
                           args.ltr_store, train_df, test_df, output_dir, precision=args.precision, analyze_explains=args.analyze_explains, max_explains=args.max_explains)
    # Given a query in --all_clicks, output to the screen all of the documents that matched this query.  Can be useful for debugging.
    if args.lookup_query:
        query = args.lookup_query
        su.lookup_query(query, all_clicks_df, opensearch, index=index_name,
                        explain=args.lookup_explain,
                        source=["name", "shortDescription", "longDescription", "salesRankShortTerm",
                                "salesRankMediumTerm", "salesRankLongTerm", "features"])
    # Given --lookup_product SKU, output that document to the terminal.  Useful for debuggging
    if args.lookup_product:
        sku = args.lookup_product
        doc = su.lookup_product(sku, opensearch, index_name)
        print("Retrieved doc:\n %s" % json.dumps(doc, indent=4))
        # opensearch.get(index_name, sku)
    # Loop through *ALL* unique SKUs from --all_clicks and validate they exist in the index by using the --lookup_product option to retrieve the document.
    # Outputs a data frame as CSV named validity.csv which tracks whether a SKU is in the index or not.  Can be used for filtering --all_clicks for training et. al.
    if args.verify_products:
        skus = all_clicks_df['sku'].drop_duplicates()
        print("Verifying %s skus.  This may take a while" % len(skus))
        sku_tracker = []
        valid_tracker = []
        status = {"sku": sku_tracker, "status": valid_tracker}
        for item in skus.iteritems():
            doc = su.lookup_product(item[1], opensearch, index_name)
            sku_tracker.append(item[1])
            if doc is None:
                valid_tracker.append(0)
            else:
                valid_tracker.append(1)
        df = pd.DataFrame(status)
        output_file = "%s/%s" % (output_dir, args.verify_file)
        print("Writing results to %s" % output_file)
        df.to_csv(output_file, index=False)
