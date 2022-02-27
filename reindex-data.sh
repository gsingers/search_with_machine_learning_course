#!/bin/sh
reindex_init () {
    PIDTEMP=`ps ux | grep logstash | grep java | awk '{ print $2 }'`
    if [ "x$PIDTEMP" = "x" ]; then
        echo "Logstash not found"
    else
         echo "Killing logstash processes ..."
         kill $PIDTEMP
    fi

    echo "Removing logstash data files ..."
    rm /workspace/logstash/logstash-7.13.2/products_data/plugins/inputs/file/.sincedb_*
    echo "Removing indices ..."
    sh delete-indexes.sh
    echo "Indexing data ..."
    sh index-data.sh -p /workspace/search_with_machine_learning_course/week2/conf/bbuy_products.json -q /workspace/search_with_machine_learning_course/week2/conf/bbuy_queries.json

}


reindex_init