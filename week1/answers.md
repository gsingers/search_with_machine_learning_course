# Answers for Week 1

### Link to your Gitpod/Github repo 

https://github.com/snikoyo/search_with_machine_learning_course


### Do your counts match ours?

- *Number of documents in the Product index: 1,275,077* : **Yes**.

- *Number of documents in the Query Log index: 1,865,269* : **Yes**

- *There are 16,772 items in the “Computers” department when using a “match all” query (“*”) and faceting on “department.keyword”* : **YES**

    I didn't need the match all query. I also didn't need the `.keyword` subfield because I only indexed it as a keyword (don't intend to search it)

    ```POST bbuy_products/_search
        "size": 0, 
        "aggs": {
            "my_agg": {
            "terms": {
                "field": "department"
            }
        }
    }```

- *Number of documents missing an “image” field: 4,434* **YES**

  Via Discover in OS Dashboards, Lucene Query Language: `NOT image:*`

  Via Query DSL: 

  ```POST bbuy_products/_search
    {
          "size": 0, 
          "query": {
          "bool": {
          "must_not": {
          "exists": {
          "field": "image"
            }
          }
        }
      }
    }```


### What field types and analyzers did you use for the following fields and why?

1. name

    I have used my own analyzer that I called "default" so that it works automatically for all the text fields. 
    
    It uses the Standard tokenizer that splits on Whitespace and Non-Alphanumeric symbols and has the following token filters:

        - english_possessive_stemmer
        - lowercase
        - english_stop
        - english_stemmer
        - lower case filter

2. shortDescription and longDescription

    Here I have used the same analyzer as for the Name field.

3. regularPrice

    This is just a double field, without analyzer. 


### Compare your Field mappings with the instructors. Where did you align and where did you differ? What are the pros and cons to the different approaches?

They seem mostly the same but I used a custom analyzer, not the English analyzer and I didn't use a suggest field. I also used my custom analyzer for all fields I imagined being useful for search,
not just name and description fields. 

### Were you able to get the “ipad 2” to show up in the top of your results? How many iterations did it take for you to get there, if at all?

Yes, but it feels like cheating because it requires knowledge in which categories (or classes in the Best Buy dataset) the "real" ipads are, so that I can boost them.

This is the query:

```
GET bbuy_products/_search
{
  "query": {
    "function_score": {
       "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "ipad 2",
            "fields": [
              "name^10.0"
            ],
            "type": "cross_fields",
            "operator": "AND",
            "slop": 0,
            "prefix_length": 0,
            "max_expansions": 50,
            "minimum_should_match": "3<80%",
            "tie_breaker": 0.1,
            "zero_terms_query": "NONE",
            "auto_generate_synonyms_phrase_query": true,
            "fuzzy_transpositions": true,
            "boost": 1.0
          }
        }
      ]
  },
      "boost": "1000", 
      "functions": [
        {
          "filter": { "match": { "class.keyword": "TABLET" } },
          "weight": 1000
        }
      ],
      "max_boost": 1000,
      "score_mode": "max",
      "boost_mode": "multiply",
      "min_score": 1
    }
  },
    "_source": {
    "includes": 
    ["categoryPath",  
    "name",
    "class"]
  },
  "sort": [
    {
      "_score": {
        "order": "desc"
      }
    },
    {
      "salesRankMediumTerm": {
        "order": "desc"
      }
    }
  ]
}
```

In a real-world ecommerce search, we would probably use the Querqy Plugin with rules curated by the product management. 
Then we would restrict the search to the "correct" category if it is only the term "ipad 2" (and not something like "ipad 2 sleeve").