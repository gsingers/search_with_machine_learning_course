#!/bin/sh
reindex_init () {
    PIDTEMP=`ps ux | grep logstash | grep java | awk '{ print $2 }'`
    if [ "x$PIDTEMP" = "x" ]; then
        echo "Logstash not found"
    else
         echo "Killing logstash processes ..."
         kill -9 $PIDTEMP
    fi

    echo "Removing logstash data files ..."
    rm /usr/local/Cellar/logstash/7.15.2/products_data/plugins/inputs/file/.sincedb_*
    echo "Removing indices ..."
    sh delete-indexes.sh
    echo "Indexing data ..."
    sh index-data.sh

}


reindex_init
