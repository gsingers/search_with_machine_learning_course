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