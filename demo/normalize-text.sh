echo "Searches with ML: AWESOMENESS!!!" \
| lmgrep --only-analyze \
         --analysis='
         {
           "analyzer": {
             "name": "english"
           }
        }' \
| jq -r '. | join(" ")'
