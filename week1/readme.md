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


## Self assesment
Team :tada:, our Week 1 Project is due by the end of the day (in your own timezone) on SUNDAY in this channel. When you submit your project, please:
- Post the link to your Gitpod/Github repo (optional - you can also submit a screenshot of your UI)
- Post your answers to the self assessment questions below
- And tag your code review partners (I will DM them to you later today)

Self Assessment Questions :male-detective:

Do your counts match ours?
- Number of documents in the Product index: 1,275,077 -> 1,274,821 (after fresh reindex)
- Number of documents in the Query Log index: 1,865,269 -> 1,865,269 (after fresh reindex)
- There are 16,772 items in the “Computers” department when using a “match all” query (“*”) and faceting on “department.keyword”. -> COMPUTERS: 16766 (aftre fresh reindex)
- Number of documents missing an “image” field: 4,434 -> 4432 (aftre fresh reindex)

What field types and analyzers did you use for the following fields and why?
- Name
  - `text` with `english`
  - `keyword` - to enable sorting by name
  - `completion` - to play around with completion, doing it on search queries could be closer to autocomplete 
  
- shortDescription and longDescription
  - `text` with `english`
  - `keyword` - just to be

- regularPrice
  - `float` for aggregationand sorting
  
- Compare your Field mappings with the instructors. Where did you align and where did you differ? What are the pros and cons to the different approaches?
  - Not a lot of difference, 

- Were you able to get the “ipad 2” to show up in the top of your results? How many iterations did it take for you to get there, if at all? (we’re not scoring this, of course, it’s just worth noting that hand tuning like this can often be quite time consuming.)
  - Yes. Few iterations, mostly I spend time on explaining how first postition weights differ from desider iPad possition. My findings are in week1 readme. 
  - Most important that term frequecy play big role, iPad accessories had much more mentions of iPad in every field, iPad had different shortDescription where it didn't mention it's name but specs.
  - I was playing with few other approches to combat terms frequecy like with slope, downbusting queries but it was hard and I gave up. Leason learn, relevance tuning is supppppppper hard.
  - Using popularity of an item break problem of relevance, but introduce popularity bias, which means more popular items are in top, which may result in them beeing purchased more offten, which in tirn will increase mid and long term rank values when index would be automaticlay update on production. 

Peer Review Questions: :handshake:
- What are 1 or 2 things they did well in the homework?
- What are 1 or 2 concrete ways they could improve their work?
- If they indicated that they were stuck and/or want focused feedback please provide responses if you can...
- Feel free to add words of encouragement as well!
