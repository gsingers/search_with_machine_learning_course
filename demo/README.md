## We can use it to normalize text in terminal

echo "Searches with ML: AWESOMENESS!!!" \
| lmgrep --only-analyze --analysis='{"analyzer": {"name": "english"}}' \
| jq -r '. | join(" ")'


## Can your text analysis be visualized

echo "search with machine learning lecture" | lmgrep --only-analyze --analysis='
{
  "token-filters": [
    {
      "name": "synonymgraph",
      "args": {
        "synonyms": "synonyms.txt",
        "expand": true
      }
    }
  ]
}
' --graph | dot -Tpng | open -a Preview.app -f

## Annotate

echo  "I am selling NIKEE" \
| lmgrep --query=“nike~” --format=json --with-details \
| jq
