####
#
#  Our main class for creating an LTR model and uploading it to OpenSearch
#
###

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
from sklearn import model_selection

# %load week2_finished/utilities/prepare_data.py
if __name__ == "__main__":
    host = 'localhost'
    port = 9200
    auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.
    parser = argparse.ArgumentParser(description='Process some integers.')

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
                          help='if set along with --generate_impressions, creates impressions based on an implied ranking in the click logs.  Writes to --impressions_file.')
    dp_group.add_argument('--generate_impressions', action="store_true",
                          help='Generate impressions by running a search and comparing results using the --all_clicks file.  Writes to --impressions_file.')
    dp_group.add_argument('--generate_num_rows', default=5000, type=int,
                          help='The number of impressions to generate using retrieval.  Randomly samples from all_clicks.  Use with --generate_impressions.  Ignored if --synthesize')
    dp_group.add_argument('--min_impressions', default=20, type=int,
                          help='The minimum number of times a query must be seen to be included in the impressions set')
    dp_group.add_argument('--min_clicks', default=10, type=int,
                          help='The minimum number of clicks a doc must have to be included in the impressions set')
    dp_group.add_argument('--query_ids', default="query_to_query_ids.json",
                          help='The name of the file to read/write under the --output_dir as JSON')
    dp_group.add_argument("-r", '--impressions_file', default="impressions.csv",
                          help='Where to write the ranks/features CSV file to.  Output is written from a Pandas data frame')

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
    xgb_group.add_argument("-t", '--create_xgb_training', action="store_true",
                           help='Create the training data set by logging the features for the training file and then outputting in RankSVM format.  Must have --train_file and --featureset')
    xgb_group.add_argument('--train_file', default="train.csv",
                           help='Where to load the training file from under the output_dir.  Required when using --create_xgb_training')

    xgb_group.add_argument("--xgb_num_training_rows", default=5000, type=int,
                           help="The number of training rows to output.  Will attempt to output a balanced set based on the grade after applying the click model.  ")
    xgb_group.add_argument("-x", '--xgb',
                           help='Train an XGB Boost model using the training file given')
    xgb_group.add_argument('--xgb_conf', default="xgb-conf.json",
                           help='Path to XGB parameters JSON dictionary.  See week2/conf/xgb-conf.json')
    xgb_group.add_argument('--xgb_feat_map', default="xgb-feat-map.txt",
                           help='File name under --output_dir containing the feature map.  Must be set when creating training data.  See week2/conf/xgb-feat-map.txt')
    xgb_group.add_argument("--xgb_rounds", default=5, help="The number of rounds to train the model on.")
    xgb_group.add_argument("--xgb_model", default="xgb_model.model",
                           help="The file name to read/write the XGB model to in --output_dir. Two files will be written: 1 with the original XBG model and 1 that is ready for uploading to LTR (name with '.ltr' appended)")
    xgb_group.add_argument("--xgb_model_name", default="ltr_model", help="The name of the model")
    xgb_group.add_argument("--xgb_plot", action="store_true",
                           help="Writes model images to the --output_dir. Requires the --xgb_model, --xgb_model_name and --xgb_feat_map args")
    xgb_group.add_argument("--xgb_test",
                           help="Given a test data set here, created separately from the train set, see how our model does!")
    xgb_group.add_argument("--xgb_diffs_output", default="xgb_test_diffs.txt",
                           help="File under --output_dir to write the differences between baseline and LTR search")

    click_group = parser.add_argument_group("Click Models")
    click_group.add_argument("--click_model", choices=["ctr", "binary", "heuristic"], default="ctr",
                             help='Simple Click-through-rate model')
    click_group.add_argument("--downsample", action="store_true",
                             help='Downsample whatever is most prevelant to create a more balanced training set.')

    split_group = parser.add_argument_group("Train/Test Splits")
    split_group.add_argument("--split_input",
                             help="If specified, will split the given file into training and testing, writing it to the file name given as an argument")
    split_group.add_argument("--split_train", default="train.csv",
                             help="The name of the training file to output under --output_dir")
    split_group.add_argument("--split_test", default="test.csv", help="The name of the test file to input")
    split_group.add_argument("--split_test_size", default=0.33, type=float, help="The name of the test file to input")
    split_group.add_argument("--split_rows", type=int, help="The total number of rows from the input file to use")

    # Some handy utilities
    util_group = parser.add_argument_group("Utilities")
    util_group.add_argument("--lookup_query",
                            help="Given a query in --all_queries, dump out all the product info for items that got clicks")
    util_group.add_argument("--lookup_explain", action="store_true",
                            help="With --lookup_query, run explains for each query/sku pair")
    util_group.add_argument("--lookup_product", help="Given a SKU, return the product")

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

    if args.split_input:
        # NOTE: Because we do some additional downsampling later, it's probably better to create slightly larger
        # Splits here than what is necessary.  We typically recommend splitting after creating the impressions
        # because otherwise you will be logging features on a lot more items
        with open(args.split_input) as input:
            print("Splitting: %s and writing train to: %s and test to: %s in %s" % (
            args.split_input, args.split_train, args.split_test, output_dir))
            input_df = pd.read_csv(args.split_input)
            input_df = input_df.sample(frac=1).reset_index(drop=True)  # shuffle things
            if args.split_rows:
                input_df = input_df[:args.split_rows]
            # sss = StratifiedShuffleSplit(n_splits=5, test_size=0.5, random_state=0)
            train, test = model_selection.train_test_split(input_df, test_size=args.split_test_size)

            train.to_csv("%s/%s" % (output_dir, args.split_train), index=False)
            test.to_csv("%s/%s" % (output_dir, args.split_test), index=False)

    ltr_store_name = args.ltr_store  # a little extra housekeeping due to the finickiness of the SLTR query
    ltr_store_path = "_ltr/" + args.ltr_store
    ltr_model_path = urljoin(base_url, ltr_store_path)
    feat_name = args.featureset_name
    # Create the LTR Store
    if args.create_ltr_store:
        ltr.create_ltr_store(ltr_model_path, auth)

    all_clicks_df = None
    if args.all_clicks:
        try:
            print("Loading all clicks from %s" % args.all_clicks)
            all_clicks_df = pd.read_csv(args.all_clicks)
            # remove sale/promotional queries like: `LaborDay_HomeAppliances_20110902`
            all_clicks_df = all_clicks_df[all_clicks_df["query"].str.match("\w+_\w+_[\w+|\d+]") == False]
        except:
            print("Error loading all clicks data")
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

    impressions_df = None
    index_name = args.index
    # Prep our data
    data_prepper = dp.DataPrepper(opensearch, feat_name, index_name, ltr_store_name)
    if args.generate_impressions:
        if all_clicks_df is None:
            print("You must provide the location of the full click log set for relevance judgments")

        if args.synthesize:
            (impressions_df, query_ids_map) = data_prepper.synthesize_impressions(all_clicks_df,
                                                                                  min_impressions=args.min_impressions,
                                                                                  min_clicks=args.min_clicks)
        else:
            # use the synthesize to feed into our generate
            (impressions_df, query_ids_map) = data_prepper.synthesize_impressions(all_clicks_df,
                                                                                  min_impressions=args.min_impressions,
                                                                                  min_clicks=args.min_clicks)
            impressions_df.drop(["product_name", "sku"], axis=1)
            impressions_df = impressions_df.sample(n=args.generate_num_rows).reset_index(drop=True)  # shuffle things
            # impressions_df = impressions_df[:args.generate_num_rows]
            (impressions_df, query_ids_map) = data_prepper.generate_impressions(impressions_df, all_clicks_df,
                                                                                query_ids_map,
                                                                                min_impressions=args.min_impressions,
                                                                                min_clicks=args.min_clicks)  # impressions as a Pandas DataFrame
        print("Writing impressions to file: %s/%s" % (output_dir, args.impressions_file))
        impressions_df.to_csv("%s/%s" % (output_dir, args.impressions_file), index=False)
        query_ids = query_ids_map
        with open("%s/%s" % (output_dir, args.query_ids), 'w') as qids:
            qids.write(json.dumps(query_ids_map))

    if args.create_xgb_training and args.train_file:
        print("Loading training from %s/%s" % (output_dir, args.train_file))
        train_df = pd.read_csv("%s/%s" % (output_dir, args.train_file))

        if train_df is not None:
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
                features_df = data_prepper.log_features(train_df, terms_field=args.ltr_terms_field)
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
                # Join the features data to the training data
                # drop the features_df doc_id, as it isn't needed anymore
                features_df.drop("doc_id", axis=1, inplace=True)
                features_df.to_csv("%s/features.csv" % output_dir)
                train_features_df = pd.merge(train_df, features_df, how="left", on=["query_id", "sku"])
                train_features_df["doc_id"] = train_features_df["sku"]

                train_features_df = cm.apply_click_model(train_features_df, args.click_model, downsample=args.downsample)
                # Now write out in XGB/SVM Rank format
                print("NAN counts: %s" % train_features_df.isna().any().count())
                train_features_df = train_features_df.fillna(0)
                train_features_df = train_features_df.sample(frac=1)  # shuffle
                ltr.write_training_file(train_features_df, "%s/training.xgb" % output_dir,
                                        "%s/%s" % (output_dir, args.xgb_feat_map))
        else:
            print("Unable to create training file, no ranks/features data available.")

    if args.xgb:
        # Defaults

        bst, xgb_params = xgbu.train(args.xgb, args.xgb_rounds, args.xgb_conf)
        print("Dumping out model using feature map: %s" % args.xgb_feat_map)
        model = bst.get_dump(fmap=("%s/%s" % (output_dir, args.xgb_feat_map)), dump_format='json')
        # Write out both the raw and the LTR ready model to disk
        # Create our metadata for uploading the model
        model_name = args.xgb_model_name
        ltr.write_opensearch_ltr_model(model_name, model, "%s/%s" % (output_dir, args.xgb_model),
                                       objective=xgb_params.get("objective", "rank:pairwise"))
        print("Saving XGB Binary model to %s/%s" % (output_dir, args.xgb_model))
        bst.save_model("%s/%s" % (output_dir, args.xgb_model))

    if args.xgb_plot:
        xgbu.plots("%s/%s" % (output_dir, args.xgb_model), args.xgb_model_name,
                   "%s/%s" % (output_dir, args.xgb_feat_map), output_dir)

    if args.xgb_test:
        # To test, we're going to calculate MAP by looking at how many "relevant" documents were in the top X of
        # our result set.
        test_data = pd.read_csv(args.xgb_test)

        (results, no_results) = su.evaluate_test_set(test_data, all_clicks_df, opensearch, args.xgb_model_name,
                                                     args.ltr_store, args.index,
                                                     output_diffs="%s/%s" % (output_dir, args.xgb_diffs_output))

    if args.lookup_query:
        query = args.lookup_query
        su.lookup_query(query, all_clicks_df, opensearch, index=index_name,
                        explain=args.lookup_explain,
                        source=["name", "shortDescription", "longDescription", "salesRankShortTerm",
                                "salesRankMediumTerm", "salesRankLongTerm", "features"])
    if args.lookup_product:
        sku = args.lookup_product
        doc = su.lookup_product(sku, opensearch, index_name)
        print("Retrieved doc:\n %s" % json.dumps(doc, indent=4))
        # opensearch.get(index_name, sku)
