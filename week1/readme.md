```
./start_week1.sh
```

## Observations for level 2
When searching for "iPad 2" I notice that explain query for productId that I was searching ("Apple® - iPad® 2 with Wi-Fi - 16GB - Black") 
Comparing diff (http://www.jsondiff.com/) between explains of first positiona and actual table position (five) shows that biggest difference was that

- iPad computer don't have `shortDescription`
- iPad accessory had one frequency occurence in name 

```
POST bbuy_products/_explain/1945531
{
  "query": {
    "bool": {
      "must": [
        {
          "query_string": {
            "query": "\"ipad 2\"",
            "fields": [
              "name^100",
              "shortDescription^50",
              "longDescription^10",
              "department"
            ]
          }
        }
      ],
      "filter": [
        {
          "term": {
            "department.keyword": "COMPUTERS"
          }
        },
        {
          "range": {
            "regularPrice": {
              "gte": "100.0",
              "lte": "1000.0"
            }
          }
        }
      ]
    }
  }
}
```

Recomgin from search departmetn and shortDescription fields change position of the iPad to 3rd
Now biggest impact has
- number of occurences in "name" field for value "2" (13 vs 10)
- number of occurences in "name" field for value "ipad" (2 vs 1)


```
POST bbuy_products/_explain/3893893
{
  "query": {
    "bool": {
      "must": [
        {
          "query_string": {
            "query": "iPad 2",
            "fields": [
              "name^100",
              "longDescription^10"
            ]
          }
        }
      ],
      "filter": [
        {
          "term": {
            "department.keyword": "COMPUTERS"
          }
        },
        {
          "range": {
            "regularPrice": {
              "gte": "100.0",
              "lte": "1000.0"
            }
          }
        }
      ]
    }
  }
}
```


This may suggest that keyword frequency may not be good indicator, let's see how search will change when phrase slope will play bigger role.
```
"phrase_slop": 2
```

Didn't change anything. 
Let's stop plaing.