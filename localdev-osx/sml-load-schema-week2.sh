#!/usr/bin/env bash
#
#
#


echo
echo "Loading products schema..."
curl -k -X PUT -u ${ES_CREDS} "https://localhost:9200/bbuy_products" -H 'Content-Type: application/json' -d "@../week2/conf/bbuy_products.json"
echo
echo

echo "Loading queries schema..."
curl -k -X PUT -u ${ES_CREDS} "https://localhost:9200/bbuy_queries" -H 'Content-Type: application/json' -d "@../week2/conf/bbuy_queries.json"
echo
echo


