#!/bin/sh
# Hat tip to Mohammadreza Alagheband

reindex_init()
{
  PIDTEMP=`ps ux | grep logstash | grep java | awk '{ print $2 }'`
  if [ "x$PIDTEMP" = "x" ]; then
    echo "Logstash not found"
  else
    echo "Logstash found: \n$PIDTEMP"
    echo "Killing logstash processes..."
    kill -9 $PIDTEMP
  fi

  echo "Removing logstash data files ..."
  rm /workspace/logstash/logstash-7.13.2/products_data/plugins/inputs/file/.sincedb_*
  
  echo "Removing indexes ..."
  sh delete-indexes.sh
  
  echo "Indexing data ..."
  sh index-data.sh
}

reindex_init
