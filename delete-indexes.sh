# WARNING: this will silently delete both of your indexes
echo "Deleting Products"
curl -k -X DELETE -u admin:admin  "https://localhost:9200/bbuy_products"
if [ $? -ne 0 ] ; then
  echo "Failed to delete products index"
  exit 2
fi
echo ""
echo "Deleting Queries"
curl -k -X DELETE -u admin:admin  "https://localhost:9200/bbuy_queries"
if [ $? -ne 0 ] ; then
  echo "Failed to delete query index"
  exit 2
fi
echo ""
echo "Deleting Annotations (may fail if it doesn't exist)"
curl -k -X DELETE -u admin:admin  "https://localhost:9200/bbuy_annotations"
# no check here, as it often fails
