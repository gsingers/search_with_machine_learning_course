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
' --graph | dot -Tpng -o greedy-synonyms.png
