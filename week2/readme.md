# Introduction to week 2
There were quite a lot of materials and technologies to get to speed in week2

Most helfull was to first go through https://elasticsearch-learning-to-rank.readthedocs.io/ documentation and setup simple learn to rank model (linera).
Bellow steps that I did


```
GET _cat/indices


GET bbuy_products/_search
{
  "_source": ["_id", "_score", "name", "salesRankLongTerm"], 
  "query": {
    "match": {
      "name": "iPad"
    }
  }
}

GET bbuy_products/_search
{
  "_source": [
    "_score",
    "name",
    "salesRankLongTerm"
  ],
  "query": {
    "function_score": {
      "query": {
        "match_all": {}
      },
      "field_value_factor": {
        "field": "salesRankLongTerm",
        "modifier": "reciprocal",
        "missing": 1000000
      }
    }
  }
}

# Enable LTR
PUT _ltr/

GET _ltr/

# Note, validation ensures that features set can be executed!
POST _ltr/_featureset/gh_feature_set
{
  "validation": {
    "params": {
      "keywords": "iPad"
    },
    "index": "bbuy_products"
  },
  "featureset": {
    "features": [
      {
        "name": "name_query",
        "params": [
          "keywords"
        ],
        "template_language": "mustache",
        "template": {
          "match": {
            "name": "{{keywords}}"
          }
        }
      }
    ]
  }
}

GET _ltr/_featureset/


POST bbuy_products/_search
{
 "size": 1,  
  "query": {
    "match_explorer": {
      "type": "stddev_raw_df",
      "query": {
        "match": {
          "name": "iPad"
        }
      }
    }
  }
}

POST bbuy_products/_search
{
  "_source": [ "name"], 
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "_id": [
              "2678269", "4382128", "1945531", "2339322"
            ]
          }
        },
        {
          "sltr": {
            "_name": "logged_gh_feature_set",
            "featureset": "gh_feature_set",
            "params": {
              "keywords": "iPad"
            }
          }
        }
      ]
    }
  },
  "ext": {
    "ltr_log": {
      "log_specs": {
        "name": "gh_log_entry1",
        "named_query": "logged_gh_feature_set"
      }
    }
  }
}

POST _ltr/_featureset/gh_feature_set/_addfeatures
{
  "features": [
    {
      "name": "sale_long_term_reciprocal",
      "params": [],
      "template_language": "mustache",
      "template": {
        "function_score": {
          "query": {
            "match_all": {}
          },
          "field_value_factor": {
            "field": "salesRankLongTerm",
            "modifier": "reciprocal",
            "missing": 1000000
          }
        }
      }
    }
  ]
}

POST _ltr/_featureset/gh_feature_set/_createmodel
{
    "model": {
        "name": "gh_linear_model",
        "model": {
            "type": "model/linear",
            "definition": "{\"name_query\" : 0.3,\"sale_long_term_reciprocal\" : 0.9}"
        }
    }
}

GET _ltr/_featureset/

# Minimal query, that use new model
POST bbuy_products/_search
{
  "_source": [
    "name"
  ],
  "query": {
    "match": {
      "name": "iPad"
    }
  },
  "rescore": {
    "query": {
      "rescore_query": {
        "sltr": {
          "params": {
            "keywords": "iPad"
          },
          "model": "gh_linear_model"
        }
      }
    },
    "window_size": 50
  }
}

# Rescoring query that also returns features map
# For potential analytic
# BTW: In bool query "filter" acts then same as "must" but score is ignored, which make sence because we're doing rescoring ourselves!
POST bbuy_products/_search
{
  "_source": [
    "name"
  ],
  "query": {
    "bool": { 
      "filter": [
        {
          "match": {
            "name": "iPad"
          }
        },
        {
          "sltr": {
            "_name": "logged_gh_feature_set",
            "featureset": "gh_feature_set",
            "params": {
              "keywords": "iPad"
            }
          }
        }
      ]
    }
  },
  "rescore": {
    "query": {
      "rescore_query": {
        "sltr": {
          "params": {
            "keywords": "iPad"
          },
          "model": "gh_linear_model"
        }
      }
    },
    "window_size": 50
  },
  "ext": {
    "ltr_log": {
      "log_specs": {
        "name": "gh_log_entry1",
        "named_query": "logged_gh_feature_set"
      }
    }
  }
}

```


## Named store
Mentions about names stores is hiden very deep

You can create named store
```
PUT _ltr/my_store
```

And then refer to it in sltr 
```
"sltr": {
    "store": "my_store"
}
```


# Self-assesment

Do you understand the steps involved in creating and deploying an LTR model? Name them and describe what each step does in your own words.
- In general whole process is very similar to ML process or Data Scientsit process. 
  Prepare data, cleans data, validate data, train model(s), compare evaluation metrics, deploy model, collect feedbback iterate.
- In our case it consist of steps like
  - Jurdgment list.
  - Enreach Jurgment list with features.
    - Enable LTR
    - Upload featureset
    - Setup OpenSearch "sltr" extension + use "stlr query"
    - Collect features from OpenSearch and add them to "xbt
  - Train & Validate.
    - Prepare training, validation and holdout dataset
    - DMatrix
  - Deploy LTR model
  - Instrument OpenSearch to take into account new model
  - Monitors and evaluate etc.

What is a feature and featureset?
- In LTR feature is a description how to extract datapoint from OpenSearch related to specific query/attributes.
- In LTR featureset is list of features that going to be extracted/or use in reranking.

What is the difference between precision and recall?
- Precission and Recall are one of many evaluation metrics. 
- In context of search.
  - Precision answer question - from search results that we identify to match "query", which are correct/relevant. 
  - Recall answer question - from search results that we identity to match "query", how many we fail to identify.
- In both cases - we have to have dataset with "correct answer" to be able to answer this question.

What are some of the traps associated with using click data in your model?
- Clicks identify which query and which product was clicked but
  - don't say on which position product was on list
  - don't say us whenver product was purchased
  - don't say how many times product was seen

What are some of the ways we are faking our data and how would you prevent that in your application?
- Collect position of clicked search result
- Collect implicit and explicit feedback
  - product was purchased
  - product was added to shopping cart
  - dwell time
  - etc

What is target leakage and why is it a bad thing?
- ML is about generalising, and leaking data makes become biased, overfit, or just usless to predicting whenever for given query (in context of search) result will be relevant to user

When can using prior history cause problems in search and LTR?
- Prior history captures some underlying distribution, trend
- When environment change, like Apple release iPad 3, then more relevant can be new product, rather than previouse generation, where we don't have prior history.
- Prior history also should be updated fairly regular, otherwise new trends may not be captured

Submit your project along with your best MRR scores:

  From ./ltr-end-to-end.sh -y

  Simple MRR is 0.300
  LTR Simple MRR is 0.608
  Hand tuned MRR is 0.445
  LTR Hand Tuned MRR is 0.638

  From ./ltr-end-to-end.sh -y -d

  Simple MRR is 0.332
  LTR Simple MRR is 0.656
  Hand tuned MRR is 0.463
  LTR Hand Tuned MRR is 0.713