# General notes not related to weekly hands-on

## Debugging Relevance

- Use the validate endpoint to understand how queries are parsed with `explain=true`

```json
# Try a simple query
GET /searchml_test/_validate/query?explain=true
{
  "query": {
      "term":{
        "title": "dog"
      }
  }
}
```

- Use the analyze endpoint to see the results of text analysis

```json
# Analyze two sentences and output detailed explanations with a custom analyzer
GET /_analyze
{
  "tokenizer" : "standard",
  "filter" : ["lowercase", "snowball"],
  "explain": "true",
  "text": ["Wearing all red, the Fox jumped out to a lead in the race over the Dog.", "All lead must be removed from the brown and red paint."]
}
```

- Use the explain endpoint to understand why a document matched a query. Alternatively, you can add `?explain=true` as query parameter when using the search endpoint.

```json
# Explain why a document matches the query
POST /searchml_test/_explain/doc_a
{
  "query": {
      "bool":{
        "must":[
            {"query_string": {
                "query": "dogs"
            }}
        ]
      }
  }
}

# Add explanations to the search results
POST /searchml_test/_search?explain=true
{
  "query": {
      "bool":{
        "must":[
            {"query_string": {
                "query": "dogs"
            }}
        ]
      }
  }
}
```

--- 

## Multi-Phase Ranking

- Rescore queries via the "rescore" function

```json
# Rework week 1 function score as a rescore
POST searchml_test/_search
{
  "query": {
      "bool": {
          "must": [
              {"match_all": {}}
          ],
          "filter": [
              {"term": {"category": "childrens"}}
          ]
      }
  },
  "rescore": {
    "query": {
      "rescore_query":{
        "function_score":{
          "field_value_factor": {
            "field": "price",
            "missing": 1
          }
        }
        
      },
      "query_weight": 1.0,
      "rescore_query_weight": 2.0
    },
    "window_size": 1 
  }
}
```

- We can also pin queries to the top. The example below pins `doc_d`

```json
# Pin results
POST searchml_test/_search
{
  "query": {
      "bool":{
        "should": [
          {
            "constant_score": {
              "filter": {"term":{"id.keyword": "doc_d"}},
              "boost": 10000
            }
          },
          {"match_all": {}}
        ]
      }
  },
  "rescore": [
    {
      "query": {
        "rescore_query":{
          "match_phrase":{
            "body":{
              "query": "Fox jumped"
            }
          }
        },
        "query_weight": 1.0,
        "rescore_query_weight": 2.0
      },
      "window_size": 2
    },
    {
      "query": {
        "rescore_query":{
          "function_score":{
            "field_value_factor": {
              "field": "price",
              "missing": 1
            }
          }
        },
        "query_weight": 1.0,
        "rescore_query_weight": 4.0
      },
      "window_size": 1
    }
  ]
}
```

- We can also run script scoring queries via OpenSearch's Painless scripting language
```json
# Script score on price for doc a
POST searchml_test/_search
{
  "query": {
      "match_all": {}
  },
  "rescore": [
    {
      "query": {
        "rescore_query":{
          "function_score":{
            "script_score": {
              "script":{
                "source": """
                if (doc['id.keyword'].value == "doc_a"){
                  return doc.price.value;
                }
                return 1;
                """
              }
            }
          }
        },
        "query_weight": 1.0,
        "rescore_query_weight": 1.0
      },
      "window_size": 10
    }
  ]
}

# Boost low cost items
POST searchml_test/_search
{
  "query": {
      "match_all": {}
  },
  "rescore": [
    {
      "query": {
        "rescore_query":{
          "function_score":{
            "functions":[
              {
                  "exp": {
                    "price":{ 
                      "origin": "0",
                    "scale": "4",
                      "decay": "0.3"
                    }
                }
              }
              ]
          }
        },
        "query_weight": 1.0,
        "rescore_query_weight": 1.0
      },
      "window_size": 10
    }
  ]
}
```

## Learning to Rank on OpenSearch

- Important to review Elastic's documentation on [Working with Features](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/building-features.html) and [Feature Engineering](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/feature-engineering.html)
    - Features are Mustache templated queries

- Query via devtools to check the featureset
```
GET _ltr/searchml_ltr/_featureset
```

- Step 4 which creates training data (aka feature logging) is the step that queries the index and gets the features
    - It requires the [`sltr`](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/logging-features.html) query to log feature values
    - Here, the term "log" is akin to querying the index, scoring each document, and "logging" the computed fields on each doc (e.g., tf-idf, bm25)

- You can alsq query for features via dev tools

```json
POST searchml_ltr/_search
{
    "query": {
        "bool": {
            "filter": [
                {
                    "terms": {
                        "_id": ["doc_a", "doc_b", "doc_c", "doc_d"]
                    }
                },
                {
                    "sltr": {
                        "_name": "logged_featureset",
                        "featureset": "ltr_toy",
                        "store": "searchml_ltr",
                        "params": {
                            "keywords": "dog"
                        }
                }}
            ]
        }
    },
    "ext": {
        "ltr_log": {
            "log_specs": {
                "name": "log_entry",
                "named_query": "logged_featureset"
            }
        }
    }
}

```

- You can retrieve the model after posting it from the model endpoint

```
GET _ltr/searchml_ltr/_model/ltr_toy_model
```

- Then, test the different results with the rescore query

```json

POST searchml_ltr/_search
{
  "query": {
    "multi_match": {
      "query": "dogs",
      "fields": [
        "title^2",
        "body"
      ]
    }
  }
}

POST searchml_ltr/_search
{
  "query": {
    "multi_match": {
      "query": "dog",
      "fields": [
        "title^2",
        "body"
      ]
    }
  },
  "rescore": {
    "window_size": 10,
    "query": {
      "rescore_query": {
        "sltr": {
          "params": {
            "keywords": "dog"
          },
          "model": "ltr_toy_model",
          "store": "searchml_ltr",
          "active_features": [
            "title_query",
            "body_query",
            "price_func"
          ]
        }
      },
      "rescore_query_weight": "2"
    }
  }
}
```