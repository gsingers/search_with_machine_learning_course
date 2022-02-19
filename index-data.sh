usage()
{
  echo "Usage: $0 [-p /path/to/bbuy/products/field/mappings] [ -q /path/to/bbuy/queries/field/mappings ] [ -b /path/to/bbuy/products/logstash/conf ] [ -e /path/to/bbuy/queries/logstash/conf ] [ -l /path/to/logstash/home ]"
  exit 2
}

PRODUCTS_JSON_FILE="/workspace/search_with_machine_learning_course/opensearch/bbuy_products.json"
QUERIES_JSON_FILE="/workspace/search_with_machine_learning_course/opensearch/bbuy_queries.json"

PRODUCTS_LOGSTASH_FILE="/workspace/search_with_machine_learning_course/logstash/index-bbuy.logstash"
QUERIES_LOGSTASH_FILE="/workspace/search_with_machine_learning_course/logstash/index-bbuy-queries.logstash"

LOGSTASH_HOME="/workspace/logstash/logstash-7.13.2"

while getopts ':p:q:b:e:l:h' c
do
  case $c in
    p) PRODUCTS_JSON_FILE=$OPTARG ;;
    q) QUERIES_JSON_FILE=$OPTARG ;;
    b) PRODUCTS_LOGSTASH_FILE=$OPTARG ;;
    e) QUERIES_LOGSTASH_FILE=$OPTARG ;;
    l) LOGSTASH_HOME=$OPTARG ;;
    h) usage ;;
    [?]) usage ;;
  esac
done
shift $((OPTIND -1))


echo "Creating index settings and mappings"
echo " Product file: $PRODUCTS_JSON_FILE"
echo " Query file: $QUERIES_JSON_FILE"
curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_products" -H 'Content-Type: application/json' -d "@$PRODUCTS_JSON_FILE"
echo ""
curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_queries" -H 'Content-Type: application/json' -d "@$QUERIES_JSON_FILE"

## Thanks to Mo: https://search-anj4074.slack.com/archives/C02TB61LU77/p1645035710531289
PIDTEMP=`ps ux | grep logstash | grep java | awk '{ print $2 }'`
if [ "x$PIDTEMP" = "x" ]; then
    echo "Logstash not found"
else
      echo "Killing logstash processes ..."
      kill -9 $PIDTEMP
fi

echo "Indexing"
echo " Product Logstash file: $PRODUCTS_LOGSTASH_FILE"
echo " Query Logstash file: $QUERIES_LOGSTASH_FILE"

echo "Running Logstash found in $LOGSTASH_HOME"
cd "$LOGSTASH_HOME"
echo "Launching Logstash indexing in the background via nohup.  See product_indexing.log and queries_indexing.log for log output"
echo " Cleaning up any old indexing information by deleting products_data.  If this is the first time you are running this, you might see an error."
rm -rf "$LOGSTASH_HOME/products_data"
nohup bin/logstash --pipeline.workers 1 --path.data ./products_data -f "$PRODUCTS_LOGSTASH_FILE" > product_indexing.log &
echo " Cleaning up any old indexing information by deleting query_data.  If this is the first time you are running this, you might see an error."
rm -rf "$LOGSTASH_HOME/query_data"
nohup bin/logstash --pipeline.workers 1 --path.data ./query_data -f "$QUERIES_LOGSTASH_FILE" > queries_indexing.log &