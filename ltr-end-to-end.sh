usage()
{
  echo "Usage: $0 [-s /workspace/search_with_machine_learning_course] [-c {ctr, heuristic, binary}] [ -w week1 ] [ -d ] [ -a /path/to/bbuy/products/train.csv ]  [-t num rows for the test split, default 100000] [-e num test queries to run. Default 200] [-r num rows for the training split, default 1000000] [-y] [-o output dir]"
  exit 2
}

SOURCE_DIR="/workspace/search_with_machine_learning_course"
WEEK="week1"
OUTPUT_DIR="/workspace/ltr_output"
ALL_CLICKS_FILE="/workspace/datasets/train.csv"
SPLIT_TRAIN_ROWS=1000000
SPLIT_TEST_ROWS=1000000
NUM_TEST_QUERIES=200 # the number of test queries to run
CLICK_MODEL="heuristic"
SYNTHESIZE=""
DOWNSAMPLE=""
while getopts ':s:c:e:w:o:a:r:t:ydh' c
do
  case $c in
    a) ALL_CLICKS_FILE=$OPTARG ;;
    c) CLICK_MODEL=$OPTARG ;;
    d) DOWNSAMPLE="--downsample" ;;
    e) NUM_TEST_QUERIES=$OPTARG ;;
    o) OUTPUT_DIR=$OPTARG ;;
    r) SPLIT_TRAIN_ROWS=$OPTARG ;;
    t) SPLIT_TEST_ROWS=$OPTARG ;;
    s) SOURCE_DIR=$OPTARG ;;
    w) WEEK=$OPTARG ;;
    y) SYNTHESIZE="--synthesize" ;;
    h) usage ;;
    [?]) usage ;;
  esac
done
shift $((OPTIND -1))


# NOTE: You must run this with the appropriate Pyenv VENV active.
# $SOURCE_DIR -- path to base of source code, eg. search_with_machine_learning/src/main/python
# $WEEK -- what week to look into
# $OUTPUT_DIR -- directory where to write output to
# $ALL_CLICKS_FILE -- The set of all clicks
cd $SOURCE_DIR
mkdir -p $OUTPUT_DIR
echo "ltr-end-to-end.sh $SOURCE_DIR $WEEK $OUTPUT_DIR $ALL_CLICKS_FILE $SYNTHESIZE $CLICK_MODEL run at "  `date` > $OUTPUT_DIR/meta.txt
set -x
python $WEEK/utilities/build_ltr.py --create_ltr_store
if [ $? -ne 0 ] ; then
  exit 2
fi
python $WEEK/utilities/build_ltr.py -f $WEEK/conf/ltr_featureset.json --upload_featureset
if [ $? -ne 0 ] ; then
  exit 2
fi
echo "Creating training and test data sets from impressions by splitting on dates"
# Split the impressions into training and test
python $WEEK/utilities/build_ltr.py --output_dir "$OUTPUT_DIR" --split_input "$ALL_CLICKS_FILE"  --split_train_rows $SPLIT_TRAIN_ROWS --split_test_rows $SPLIT_TEST_ROWS
if [ $? -ne 0 ] ; then
  exit 2
fi

# Create our impressions (positive/negative) data set, e.g. all sessions (with LTR features added in already)
echo "Creating impressions data set" # outputs to $OUTPUT_DIR/impressions.csv by default
python $WEEK/utilities/build_ltr.py --generate_impressions  --output_dir "$OUTPUT_DIR" --train_file "$OUTPUT_DIR/train.csv" $SYNTHESIZE
if [ $? -ne 0 ] ; then
  exit 2
fi
# Create the actual training set from the impressions set
python $WEEK/utilities/build_ltr.py --ltr_terms_field sku --output_dir "$OUTPUT_DIR" --create_xgb_training -f $WEEK/conf/ltr_featureset.json --click_model $CLICK_MODEL $DOWNSAMPLE
if [ $? -ne 0 ] ; then
  exit 2
fi
# Given a training set in SVMRank format, train an XGB model
python $WEEK/utilities/build_ltr.py  --output_dir "$OUTPUT_DIR" -x "$OUTPUT_DIR/training.xgb" --xgb_conf $WEEK/conf/xgb-conf.json
if [ $? -ne 0 ] ; then
  exit 2
fi
# Given an XGB model, upload it to the LTR store
python $WEEK/utilities/build_ltr.py --upload_ltr_model --xgb_model "$OUTPUT_DIR/xgb_model.model"
if [ $? -ne 0 ] ; then
  exit 2
fi
# Dump out some useful plots for visualizing our model
python $WEEK/utilities/build_ltr.py --xgb_plot --output_dir "$OUTPUT_DIR"
if [ $? -ne 0 ] ; then
  exit 2
fi
# Run our test queries through
python $WEEK/utilities/build_ltr.py --xgb_test "$OUTPUT_DIR/test.csv" --train_file "$OUTPUT_DIR/train.csv" --output_dir "$OUTPUT_DIR" --xgb_test_num_queries $NUM_TEST_QUERIES  --xgb_main_query 0
if [ $? -ne 0 ] ; then
  exit 2
fi
# Analyze the results
python $WEEK/utilities/build_ltr.py --analyze --output_dir "$OUTPUT_DIR" 