usage()
{
  echo "Usage: $0 [-y /path/to/python/indexing/code] [-d /path/to/kaggle/best/buy/datasets] [-p /path/to/bbuy/products/field/mappings] [-n ] [-a /path/to/bbuy/product annotations/field/mappings] [ -q /path/to/bbuy/queries/field/mappings ] [ -g /path/to/write/logs/to ]"
  echo "if -n is specified, then ONLY annotations indexing (week 2 content) will be done"
  echo "Synonyms are ONLY applied to the annotation indexing (-n), which is on a reduced set of results"
  echo "Example: ./index-data.sh  -y /Users/grantingersoll/projects/corise/search_ml_instructor/src/main/python/search_ml/week1_finished   -d /Users/grantingersoll/projects/corise/datasets/bbuy -q /Users/grantingersoll/projects/corise/search_ml_instructor/src/main/conf/bbuy_queries.json -p /Users/grantingersoll/projects/corise/search_ml_instructor/src/main/conf/bbuy_products.json -g /tmp"
  exit 2
}

ANNOTATIONS_JSON_FILE="/workspace/search_with_machine_learning_course/conf/bbuy_annotations.json"
PRODUCTS_JSON_FILE="/workspace/search_with_machine_learning_course/conf/bbuy_products.json"
QUERIES_JSON_FILE="/workspace/search_with_machine_learning_course/conf/bbuy_queries.json"
DATASETS_DIR="/workspace/datasets"
PYTHON_LOC="/workspace/search_with_machine_learning_course/utilities"

LOGS_DIR="/workspace/logs"
ANNOTATE=""
while getopts ':p:a:q:g:y:d:hrn' c
do
  case $c in
    a) ANNOTATIONS_JSON_FILE=$OPTARG ;;
    p) PRODUCTS_JSON_FILE=$OPTARG ;;
    q) QUERIES_JSON_FILE=$OPTARG ;;
    d) DATASETS_DIR=$OPTARG ;;
    g) LOGS_DIR=$OPTARG ;;
    y) PYTHON_LOC=$OPTARG ;;
    n) ANNOTATE="--annotate" ;;
    r) REDUCE="--reduced" ;;
    h) usage ;;
    [?])
      echo "Invalid option: -${OPTARG}"
      usage ;;
  esac
done
shift $((OPTIND -1))

mkdir $LOGS_DIR

cd $PYTHON_LOC || exit
echo "Running python scripts from $PYTHON_LOC"

set -x

if [ "$ANNOTATE" != "--annotate" ]; then
  echo "Creating index settings and mappings"
  if [ -f $PRODUCTS_JSON_FILE ]; then
    echo " Product file: $PRODUCTS_JSON_FILE"
    curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_products" -H 'Content-Type: application/json' -d "@$PRODUCTS_JSON_FILE"
    if [ $? -ne 0 ] ; then
      echo "Failed to create index with settings of $PRODUCTS_JSON_FILE"
      exit 2
    fi

    if [ -f index_products.py ]; then
      echo "Indexing product data in $DATASETS_DIR/product_data/products and writing logs to $LOGS_DIR/index_products.log"
      nohup python index_products.py $REDUCE -s "$DATASETS_DIR/product_data/products" > "$LOGS_DIR/index_products.log" &
      if [ $? -ne 0 ] ; then
        echo "Failed to index products"
        exit 2
      fi
    fi
  fi

  if [ -f $QUERIES_JSON_FILE ]; then
    echo ""
    echo " Query file: $QUERIES_JSON_FILE"
    curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_queries" -H 'Content-Type: application/json' -d "@$QUERIES_JSON_FILE"
    if [ $? -ne 0 ] ; then
      echo "Failed to create index with settings of $QUERIES_JSON_FILE"
      exit 2
    fi
    if [ -f index_queries.py ]; then
      echo "Indexing queries data and writing logs to $LOGS_DIR/index_queries.log"
      nohup python index_queries.py -s "$DATASETS_DIR/train.csv" > "$LOGS_DIR/index_queries.log" &
      if [ $? -ne 0 ] ; then
        echo "Failed to index queries"
        exit 2
      fi
    fi
  fi
fi

if [ "$ANNOTATE" == "--annotate" ]; then
  echo "Creating Annotations index"
  if [ -f $ANNOTATIONS_JSON_FILE ]; then
    echo " Product Annotations file: $ANNOTATIONS_JSON_FILE"
    curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_annotations" -H 'Content-Type: application/json' -d "@$ANNOTATIONS_JSON_FILE"
    if [ $? -ne 0 ] ; then
      echo "Failed to create index with settings of $ANNOTATIONS_JSON_FILE"
      exit 2
    fi
    echo ""
    if [ -f index_products.py ]; then
      echo "Indexing product annotations data in $DATASETS_DIR/product_data/products and writing logs to $LOGS_DIR/index_annotations.log"
      nohup python index_products.py "--synonyms" "--reduced" --index_name "bbuy_annotations" -s "$DATASETS_DIR/product_data/products" > "$LOGS_DIR/index_annotations.log" &
      if [ $? -ne 0 ] ; then
        echo "Failed to index product annotations"
        exit 2
      fi
    fi
  fi
fi



