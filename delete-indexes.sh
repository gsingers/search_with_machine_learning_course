# WARNING: this will silently delete both of your indexes

curl -k -X DELETE -u admin  "https://localhost:9200/bbuy_products"
curl -k -X DELETE -u admin  "https://localhost:9200/bbuy_queries"
curl -k -X DELETE -u admin  "https://localhost:9200/bbuy_annotations"
