# Answers for Week 1

### Link to your Gitpod/Github repo 

https://github.com/snikoyo/search_with_machine_learning_course

### Screenshot of UI

TODO

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

1. Name

    I have used 

2. shortDescription and longDescription

    Here I have used the same analyzer as for the Name field.

3. regularPrice

    This is just a double field, without analyzer. 


### Compare your Field mappings with the instructors. Where did you align and where did you differ? What are the pros and cons to the different approaches?

TODO **Were are the instructors field mappings?**

### Were you able to get the “ipad 2” to show up in the top of your results? How many iterations did it take for you to get there, if at all?

TODO