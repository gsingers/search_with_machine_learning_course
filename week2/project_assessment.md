1. For classifying product names to categories:

- What precision (P@1) were you able to achieve?

| Metric | Score |
|---:|---|
N | 1000
P@1 | 0.971
R@1 | 0.971

- What fastText parameters did you use?

| Parameters | Value |
|---:|---|
learning rate | 1
epoch | 25
wordNgrams | 2

- How did you transform the product names?

  - Remove all non-alphanumeric characters other than underscore
  - Trimmed excess space characters so that tokens are separated by a single space
  - Convert all letters to lowercase and remove surround whitespace
  - Applied Snowball stemmer

This increased precision from 0.6 to 0.614

- How did you prune infrequent category labels, and how did that affect your precision?

I removed all categories with fewer than 500 products in them. This increased precision from 
0.614 to 0.971

- How did you prune the category tree, and how did that affect your precision?

TODO

2. For deriving synonyms from content:

- What were the results for your best model in the tokens used for evaluation?

The best model had an average loss of 1.9213

- What fastText parameters did you use?

| Parameters | Value |
|---:|---|
learning rate | -
epoch | 2
wordNgrams | 2

Setting the lr causes an error `fasttext::DenseMatrix::EncounteredNaNError`

- How did you transform the product names?

Raw titles were used, only extra spaces were removed.

3. For integrating synonyms with search:

- How did you transform the product names (if different than previously)?

```json
...
      "name": {
        "type": "text",
        "analyzer": "english",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 2048
          },
          "hyphens": {
            "type": "text",
            "analyzer": "smarter_hyphens"
          },
          "suggest": {
            "type": "completion"
          },
          "synonyms": {
              "type": "text",
              "analyzer": "synonym"
          }
        }
      }
...
```

Call to test the synonym analyzer:

- Request:
```json
GET /bbuy_products/_analyze
{
  "analyzer": "synonym",
  "explain": "true",
  "text": ["earbuds"]
}

{
  "detail" : {
    "custom_analyzer" : true,
    "charfilters" : [ ],
    "tokenizer" : {
      "name" : "whitespace",
      "tokens" : [
        {
          "token" : "earbuds",
          "start_offset" : 0,
          "end_offset" : 7,
          "type" : "word",
          "position" : 0,
          "bytes" : "[65 61 72 62 75 64 73]",
          "positionLength" : 1,
          "termFrequency" : 1
        }
      ]
    },
    "tokenfilters" : [
      {
        "name" : "stemmer",
        "tokens" : [
          {
            "token" : "earbud",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "word",
            "position" : 0,
            "bytes" : "[65 61 72 62 75 64]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          }
        ]
      },
      {
        "name" : "synonym",
        "tokens" : [
          {
            "token" : "earbud",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "word",
            "position" : 0,
            "bytes" : "[65 61 72 62 75 64]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "headphon",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[68 65 61 64 70 68 6f 6e]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "ear",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[65 61 72]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "yurbud",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[79 75 72 62 75 64]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "earphon",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[65 61 72 70 68 6f 6e]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "stereophon",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[73 74 65 72 65 6f 70 68 6f 6e]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "earpollut",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[65 61 72 70 6f 6c 6c 75 74]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "bud",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[62 75 64]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "2xl",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[32 78 6c]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "skullcandi",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[73 6b 75 6c 6c 63 61 6e 64 69]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "skullcrush",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[73 6b 75 6c 6c 63 72 75 73 68]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "skull",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[73 6b 75 6c 6c]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "hesh",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[68 65 73 68]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          },
          {
            "token" : "smokin",
            "start_offset" : 0,
            "end_offset" : 7,
            "type" : "SYNONYM",
            "position" : 0,
            "bytes" : "[73 6d 6f 6b 69 6e]",
            "keyword" : false,
            "positionLength" : 1,
            "termFrequency" : 1
          }
        ]
      }
    ]
  }
}
```

- What threshold score did you use?

0.75

- Were you able to find the additional results by matching synonyms?

| Query | # Results w/o synonyms | # Results w/ synonyms
|---:|---|
earbuds | 1205 | 3668
nespresso | 8 | 495
dslr | 2837 | 2813

4. For classifying reviews:

TODO

- What precision (P@1) were you able to achieve?

- What fastText parameters did you use?

- How did you transform the review content?

- What else did you try and learn?