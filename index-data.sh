echo "Creating index settings and mappings"
curl -k -X PUT -u admin  "https://localhost:9200/_template/bbuy_products" -H 'Content-Type: application/json' -d /workspace/search_with_machine_learning_course/opensearch/bbuy_products.json
curl -k -X PUT -u admin  "https://localhost:9200/_template/bbuy_queries" -H 'Content-Type: application/json' -d /workspace/search_with_machine_learning_course/opensearch/bbuy_queries.json

cd /workspace/search_with_machine_learning_course/logstash-7.13.2/
echo "Launching Logstash indexing in the background via nohup.  See product_indexing.log and queries_indexing.log for log output"
nohup bin/logstash --path.data ./products_data -f $SEARCH_DIR/search_course/src/main/logstash/index-bbuy.logstash > product_indexing.log &

nohup bin/logstash --path.data ./products_data -f $SEARCH_DIR/search_course/src/main/logstash/index-bbuy-queries.logstash > queries_indexing.log &