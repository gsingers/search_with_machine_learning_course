echo  "I am selling NIKEE" \
| lmgrep --query=“nike~” --format=json --with-details \
| jq