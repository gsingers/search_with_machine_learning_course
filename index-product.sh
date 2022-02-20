PRODUCTS_JSON_FILE="/workspace/search_with_machine_learning_course/opensearch/bbuy_products.json"
PRODUCTS_LOGSTASH_FILE="/workspace/search_with_machine_learning_course/logstash/index-bbuy.logstash"
LOGSTASH_HOME="/workspace/logstash/logstash-7.13.2"

echo "Creating index settings and mappings"
echo " Product file: $PRODUCTS_JSON_FILE"
curl -k -X PUT -u admin:admin  "https://localhost:9200/bbuy_products" -H 'Content-Type: application/json' -d "@$PRODUCTS_JSON_FILE"

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

echo "Running Logstash found in $LOGSTASH_HOME"
cd "$LOGSTASH_HOME"
echo "Launching Logstash indexing in the background via nohup.  See product_indexing.log and queries_indexing.log for log output"
echo " Cleaning up any old indexing information by deleting products_data.  If this is the first time you are running this, you might see an error."
rm -rf "$LOGSTASH_HOME/products_data"
nohup bin/logstash --pipeline.workers 1 --path.data ./products_data -f "$PRODUCTS_LOGSTASH_FILE" > product_indexing.log &