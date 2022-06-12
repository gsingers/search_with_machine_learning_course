usage()
{
  echo "Usage: $0 [-y /path/to/python/indexing/code] [-d /path/to/kaggle/best/buy/datasets] [-p /path/to/bbuy/products/field/mappings] [ -q /path/to/bbuy/queries/field/mappings ] [ -g /path/to/write/logs/to ]"
  echo "Example: ./index-data.sh  -y /Users/grantingersoll/projects/corise/search_ml_instructor/src/main/python/search_ml/week1_finished   -d /Users/grantingersoll/projects/corise/datasets/bbuy -q /Users/grantingersoll/projects/corise/search_ml_instructor/src/main/conf/bbuy_queries.json -p /Users/grantingersoll/projects/corise/search_ml_instructor/src/main/conf/bbuy_products.json -g /tmp"
  exit 2
}

PRODUCTS_JSON_FILE="/workspace/search_with_machine_learning_course/conf/bbuy_products.json"
QUERIES_JSON_FILE="/workspace/search_with_machine_learning_course/conf/bbuy_queries.json"
DATASETS_DIR="/workspace/datasets"
PYTHON_LOC="/workspace/search_with_machine_learning_course/utilities"

LOGS_DIR="/workspace/logs"

while getopts ':p:q:g:y:d:h:r' c
do
  case $c in
    p) PRODUCTS_JSON_FILE=$OPTARG ;;
    q) QUERIES_JSON_FILE=$OPTARG ;;
    d) DATASETS_DIR=$OPTARG ;;
    g) LOGS_DIR=$OPTARG ;;
    y) PYTHON_LOC=$OPTARG ;;
    r) REDUCE="--reduced" ;;
    h) usage ;;
    [?]) usage ;;
  esac
done
shift $((OPTIND -1))

mkdir $LOGS_DIR

echo "Creating index settings and mappings"
echo " Product file: $PRODUCTS_JSON_FILE"
curl -k -X PUT -u admin  "https://localhost:9200/bbuy_products" -H 'Content-Type: application/json' -d "@$PRODUCTS_JSON_FILE"
echo ""
echo " Query file: $QUERIES_JSON_FILE"
curl -k -X PUT -u admin  "https://localhost:9200/bbuy_queries" -H 'Content-Type: application/json' -d "@$QUERIES_JSON_FILE"

echo "Running indexers located in $PYTHON_LOC"
cd $PYTHON_LOC
echo ""
if [ -f index_products.py ]; then
  echo "Indexing product data in $DATASETS_DIR/product_data/products and writing logs to $LOGS_DIR/index_products.log"
  nohup python index_products.py $REDUCE -s "$DATASETS_DIR/product_data/products" > "$LOGS_DIR/index_products.log" &
  if [ $? -ne 0 ] ; then
    echo "Failed to index products"
    exit 2
  fi
fi
if [ -f index_queries.py ]; then
  echo "Indexing queries data and writing logs to $LOGS_DIR/index_queries.log"
  nohup python index_queries.py -s "$DATASETS_DIR/train.csv" > "$LOGS_DIR/index_queries.log" &
  if [ $? -ne 0 ] ; then
    echo "Failed to index queries"
    exit 2
  fi
fi
