# Notes for Week 1

Install and jupyter for interactive exploration of data
```bash
# Install jupyter if not added to dockerfile
pyenv activate search_with_ml
/home/gitpod/.pyenv/versions/3.9.7/envs/search_with_ml/bin/python3.9 -m pip install jupyter

# Start jupyter notebook in env
jupyter notebook

# Once done, it should return a localhost URL with a token attached like below. Copy it
# http://localhost:8888/?token=36dfe17645d158373a1adcaac1deaeouaoeueoauaoeueouaeouaoeu

# When you try to run the first cell on the notebook, it'll prompt you to provide a server
# Enter the URL you copied and profit. That said, running in VSCode doesn't have autocomplete
# and a few other bells and whistles. Thus, I'm still mostly using jupyter on browser.
```

What do do if we don't have impression data? We can generate synthetic impressions via two methods:
- Run queries via baseline retrieval that will collect the full set of impressions and join them with clicks, or
  - Assumes that baseline retrieval is roughly equivalent to the logging policy (used when collecting the click data)
- Infer the ranking based on click distribution (i.e., more clicks = higher ranking)
  - Assumes that more clicks = higher ranking in the logged policy

How to check LTR features via dev tools
```json
GET bbuy_products/_search
{
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "sku": [2052194, 2053166, 8523243, 9311586]
          }
        },
        {
          "sltr": {
            "_name": "logged_featureset",
            "featureset": "bbuy_main_featureset",
            "store": "week1",
            "params": {
              "keywords": "yamaha"
            }
          }
        }
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

Iterating on features and models
```bash
# To run everything end-to-end
./ltr-end-to-end.sh -y
```

```bash
# To just evaluate LTR
python week1/utilities/build_ltr.py --xgb_test /workspace/ltr_output/test.csv --train_file /workspace/ltr_output/train.csv --output_dir /workspace/ltr_output --xgb_test_num_queries 200 && python week1/utilities/build_ltr.py --analyze --output_dir /workspace/ltr_output

Simple MRR is 0.282
LTR Simple MRR is 0.283
Hand tuned MRR is 0.408
LTR Hand Tuned MRR is 0.405

Simple p@10 is 0.113
LTR simple p@10 is 0.114
Hand tuned p@10 is 0.160
LTR hand tuned p@10 is 0.158
Simple better: 117      LTR_Simple Better: 42   Equal: 1972
HT better: 783  LTR_HT Better: 616      Equal: 952
Saving Better/Equal analysis to /workspace/ltr_output/analysis
```

```bash
# Equal weight between LTR and main
python week1/utilities/build_ltr.py --xgb_test /workspace/ltr_output/test.csv --train_file /workspace/ltr_output/train.csv --output_dir /workspace/ltr_output --xgb_test_num_queries 200 --xgb_main_query_weight 1 --xgb_rescore_query_weight 1 && python week1/utilities/build_ltr.py --analyze --output_dir /workspace/ltr_output

Simple MRR is 0.282
LTR Simple MRR is 0.282
Hand tuned MRR is 0.408
LTR Hand Tuned MRR is 0.407

Simple p@10 is 0.113
LTR simple p@10 is 0.114
Hand tuned p@10 is 0.160
LTR hand tuned p@10 is 0.161
Simple better: 92       LTR_Simple Better: 40   Equal: 1999
HT better: 716  LTR_HT Better: 580      Equal: 1055
```

```bash
# LTR weight = 1000
python week1/utilities/build_ltr.py --xgb_test /workspace/ltr_output/test.csv --train_file /workspace/ltr_output/train.csv --output_dir /workspace/ltr_output --xgb_test_num_queries 200 --xgb_main_query_weight 1 --xgb_rescore_query_weight 1000 && python week1/utilities/build_ltr.py --analyze --output_dir /workspace/ltr_output

Simple MRR is 0.282
LTR Simple MRR is 0.268
Hand tuned MRR is 0.408
LTR Hand Tuned MRR is 0.364

Simple p@10 is 0.113
LTR simple p@10 is 0.107
Hand tuned p@10 is 0.160
LTR hand tuned p@10 is 0.136
Simple better: 621      LTR_Simple Better: 243  Equal: 1267
HT better: 1202 LTR_HT Better: 748      Equal: 401
```

```bash
# Main weight = 1000
python week1/utilities/build_ltr.py --xgb_test /workspace/ltr_output/test.csv --train_file /workspace/ltr_output/train.csv --output_dir /workspace/ltr_output --xgb_test_num_queries 200 --xgb_main_query_weight 1000 --xgb_rescore_query_weight 1 && python week1/utilities/build_ltr.py --analyze --output_dir /workspace/ltr_output

Simple MRR is 0.282
LTR Simple MRR is 0.282
Hand tuned MRR is 0.408
LTR Hand Tuned MRR is 0.408

Simple p@10 is 0.113
LTR simple p@10 is 0.113
Hand tuned p@10 is 0.160
LTR hand tuned p@10 is 0.160
Simple better: 0        LTR_Simple Better: 0    Equal: 2131
HT better: 155  LTR_HT Better: 194      Equal: 2002
```

```bash
# No main, default to LTR
python week1/utilities/build_ltr.py --xgb_test /workspace/ltr_output/test.csv --train_file /workspace/ltr_output/train.csv --output_dir /workspace/ltr_output --xgb_test_num_queries 200 --xgb_main_query_weight 0 --xgb_rescore_query_weight 1 && python week1/utilities/build_ltr.py --analyze --output_dir /workspace/ltr_output

Simple MRR is 0.282
LTR Simple MRR is 0.161
Hand tuned MRR is 0.408
LTR Hand Tuned MRR is 0.161

Simple p@10 is 0.113
LTR simple p@10 is 0.058
Hand tuned p@10 is 0.160
LTR hand tuned p@10 is 0.062
Simple better: 1193     LTR_Simple Better: 915  Equal: 23
HT better: 1452 LTR_HT Better: 878      Equal: 21
```

## Run everything with main query weight = 0

With default feature of name match

```bash
./ltr-end-to-end.sh -y -m 0 -c quantiles

Simple MRR is 0.285
LTR Simple MRR is 0.199
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.195

Simple p@10 is 0.119
LTR simple p@10 is 0.087
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.089
Simple better: 647      LTR_Simple Better: 458  Equal: 14
HT better: 680  LTR_HT Better: 597      Equal: 15
```

With name_match_phrase on name.hyphens
```bash
./ltr-end-to-end.sh -y -m 0 -c quantiles

Simple MRR is 0.285
LTR Simple MRR is 0.250
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.268

Simple p@10 is 0.119
LTR simple p@10 is 0.098
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.113
Simple better: 642      LTR_Simple Better: 463  Equal: 14
HT better: 663  LTR_HT Better: 617      Equal: 12
```

With customer_review_average
```bash
./ltr-end-to-end.sh -y -m 0 -c quantiles

Simple MRR is 0.285
LTR Simple MRR is 0.275
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.268

Simple p@10 is 0.119
LTR simple p@10 is 0.101
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.096
Simple better: 631      LTR_Simple Better: 483  Equal: 5
HT better: 773  LTR_HT Better: 512      Equal: 7
```

With customer_review_count
```bash
./ltr-end-to-end.sh -y -m 0 -c quantiles

Simple MRR is 0.285
LTR Simple MRR is 0.350
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.299

Simple p@10 is 0.119
LTR simple p@10 is 0.125
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.137
Simple better: 535      LTR_Simple Better: 569  Equal: 15
HT better: 621  LTR_HT Better: 662      Equal: 9
```

With artist_name_match_phrase
```bash
./ltr-end-to-end.sh -y -m 0 -c quantiles

Simple MRR is 0.285
LTR Simple MRR is 0.309
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.293

Simple p@10 is 0.119
LTR simple p@10 is 0.137
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.136
Simple better: 500      LTR_Simple Better: 608  Equal: 11
HT better: 596  LTR_HT Better: 684      Equal: 12
```

With long and short_desc match phrase
```bash
./ltr-end-to-end.sh -y -m 0 -c quantiles

Simple MRR is 0.285
LTR Simple MRR is 0.309
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.293

Simple p@10 is 0.119
LTR simple p@10 is 0.137
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.136
Simple better: 500      LTR_Simple Better: 608  Equal: 11
HT better: 596  LTR_HT Better: 684      Equal: 12
```

### BEST RESULT
```python
features = [
            'name_match', 'name_match_phrase', 
            'customer_review_average', 'customer_review_count',
            'artist_name_match_phrase',
            'short_desc_match_phrase', 'long_desc_match_phrase',
            'sales_rank_short_term'
            ]

# ./ltr-end-to-end.sh -y -m 0 -c quantiles

# Simple MRR is 0.285
# LTR Simple MRR is 0.448
# Hand tuned MRR is 0.423
# LTR Hand Tuned MRR is 0.464

# Simple p@10 is 0.119
# LTR simple p@10 is 0.167
# Hand tuned p@10 is 0.171
# LTR hand tuned p@10 is 0.190
# Simple better: 467      LTR_Simple Better: 637  Equal: 15
# HT better: 555  LTR_HT Better: 717      Equal: 20
```

```python
features = [
            'name_match', 'name_match_phrase', 
            'customer_review_average', 'customer_review_count',
            'artist_name_match_phrase',
            'short_desc_match_phrase', 'long_desc_match_phrase',
            'sales_rank_short_term', 'sales_rank_medium_term', 'sales_rank_long_term',
            'sale_price', 'on_sale'
            ]

# ./ltr-end-to-end.sh -y -m 0 -c quantiles

# Simple MRR is 0.285
# LTR Simple MRR is 0.396
# Hand tuned MRR is 0.423
# LTR Hand Tuned MRR is 0.404

# Simple p@10 is 0.119
# LTR simple p@10 is 0.138
# Hand tuned p@10 is 0.171
# LTR hand tuned p@10 is 0.143
# Simple better: 517      LTR_Simple Better: 591  Equal: 11
# HT better: 640  LTR_HT Better: 630      Equal: 22
```

```python
features = [
            'name_match', 'name_match_phrase', 
            'name_match_phrase_near_exact', 'multi_match',
            'customer_review_average', 'customer_review_count',
            'short_desc_match_phrase', 'long_desc_match_phrase',
            'sales_rank_short_term', 'sales_rank_medium_term', 
            ]

# ./ltr-end-to-end.sh -y -m 0 -c quantiles

# Simple MRR is 0.285
# LTR Simple MRR is 0.365
# Hand tuned MRR is 0.423
# LTR Hand Tuned MRR is 0.361

# Simple p@10 is 0.119
# LTR simple p@10 is 0.121
# Hand tuned p@10 is 0.171
# LTR hand tuned p@10 is 0.121
# Simple better: 515      LTR_Simple Better: 593  Equal: 11
# HT better: 690  LTR_HT Better: 592      Equal: 10
```

## Exploring data

- The data's not as clean as we would like, with missing values for important values such as short, medium, and long term rank.
- Also, there are a lot of tail queries. These are excluded if they do not have ≥ 20 impressions and ≥ 5 clicks.

## Debugging LTR

- Evaluation and analysis of results is done in `search_utils.py`
- We can also get raw term statistics as features via [`match_explorer`](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/feature-engineering.html#getting-raw-term-statistics)


```python
# Querying for raw term statistics
query_obj = {
    'query': {
        'match_explorer': {
            'type': 'mean_raw_tf',
            'query': {
                'match': {
                    'name': 'iphone'
                }
            }
        }
    },
    '_source': ['name']
}

client.search(body=query_obj, index='bbuy_products')['hits']['hits'][:3]

[{'_index': 'bbuy_products',
  '_id': '3812736',
  '_score': 2.0,
  '_source': {'name': ['OtterBox - Commuter Series Case for Apple® iPhone® 4 and 4S\n\n iPhone 4S - Gunmetal Gray/Yellow']}},
 {'_index': 'bbuy_products',
  '_id': '3869388',
  '_score': 2.0,
  '_source': {'name': ['Belkin - Essential 050 Case for Apple® iPhone® 4 and iPhone 4S - Pink/Purple']}},
 {'_index': 'bbuy_products',
  '_id': '3869439',
  '_score': 2.0,
  '_source': {'name': ['Belkin - Essential 050 Case for Apple® iPhone® 4 and iPhone 4S - Blue/White']}}]
```

- If we want to get all features, we can use the explain query

```python
# Querying for explain statistics
query_obj = {
    'query': {
        'match': {
            'name': 'iphone'
        }
    }
}

response = client.explain(id='4095076', body=query_obj, index='bbuy_products')

response['explanation']['details']

[{'value': 6.739648,
  'description': 'score(freq=2.0), computed as boost * idf * tf from:',
  'details': [{'value': 2.2, 'description': 'boost', 'details': []},
   {'value': 6.744475,
    'description': 'idf, computed as log(1 + (N - n + 0.5) / (n + 0.5)) from:',
    'details': [{'value': 1500,
      'description': 'n, number of documents containing term',
      'details': []},
     {'value': 1274453,
      'description': 'N, total number of documents with field',
      'details': []}]},
   {'value': 0.45422012,
    'description': 'tf, computed as freq / (freq + k1 * (1 - b + b * dl / avgdl)) from:',
    'details': [{'value': 2.0,
      'description': 'freq, occurrences of term within document',
      'details': []},
     {'value': 1.2,
      'description': 'k1, term saturation parameter',
      'details': []},
     {'value': 0.75,
      'description': 'b, length normalization parameter',
      'details': []},
     {'value': 12.0, 'description': 'dl, length of field', 'details': []},
     {'value': 5.1351514,
      'description': 'avgdl, average length of field',
      'details': []}]}]}]
```

## Using prior query history
- I.e., Using the clicks from prior queries to predict future query results.
- This comes with the cold-start problem where a new product that's not clicked in historical data will not be predicted because the model hasn't seen this product.
- One way around this is to have good item representations. For example, the features we use on name match, description match, are a representation of the item. Alternatively, content embedding (which is similar to text matching features).
- Using prior query history significantly outperforms best result without it.
```python
features = [
            'name_match', 'name_match_phrase', 
            'customer_review_average', 'customer_review_count',
            'artist_name_match_phrase',
            'short_desc_match_phrase', 'long_desc_match_phrase',
            'sales_rank_short_term',
            'click_prior'  # Additional feature
            ]

# ./ltr-end-to-end.sh -y -m 0 -c quantiles

# Simple MRR is 0.285
# LTR Simple MRR is 0.634
# Hand tuned MRR is 0.423
# LTR Hand Tuned MRR is 0.710

# Simple p@10 is 0.119
# LTR simple p@10 is 0.313
# Hand tuned p@10 is 0.171
# LTR hand tuned p@10 is 0.355
# Simple better: 412      LTR_Simple Better: 695  Equal: 12
# HT better: 521  LTR_HT Better: 750      Equal: 21

# PREVIOUS BEST RESULT
features = [
            'name_match', 'name_match_phrase', 
            'customer_review_average', 'customer_review_count',
            'artist_name_match_phrase',
            'short_desc_match_phrase', 'long_desc_match_phrase',
            'sales_rank_short_term'
            ]

# ./ltr-end-to-end.sh -y -m 0 -c quantiles

# Simple MRR is 0.285
# LTR Simple MRR is 0.448
# Hand tuned MRR is 0.423
# LTR Hand Tuned MRR is 0.464

# Simple p@10 is 0.119
# LTR simple p@10 is 0.167
# Hand tuned p@10 is 0.171
# LTR hand tuned p@10 is 0.190
# Simple better: 467      LTR_Simple Better: 637  Equal: 15
# HT better: 555  LTR_HT Better: 717      Equal: 20
```

- Checking query object (Looks correct where it's a proportion from 0 - 1 and not an absolute value)

```
{"size": 500, "sort": [{"_score": {"order": "desc"}}], "query": {"bool": {"must": [], "should": [{"match": {"name": {"query": "lcd monitor", "fuzziness": "1", "prefix_length": 2, "boost": 0.01}}}, {"match_phrase": {"name.hyphens": {"query": "lcd monitor", "slop": 1, "boost": 50}}}, {"multi_match": {"query": "lcd monitor", "type": "phrase", "slop": "6", "minimum_should_match": "2<75%", "fields": ["name^10", "name.hyphens^10", "shortDescription^5", "longDescription^5", "department^0.5", "sku", "manufacturer", "features", "categoryPath"]}}, {"terms": {"sku": ["lcd", "monitor"], "boost": 50.0}}, {"match": {"name.hyphens": {"query": "lcd monitor", "operator": "OR", "minimum_should_match": "2<75%"}}}, {"query_string": {"query": "9346861^0.041  2596077^0.054  7662095^0.014  2815266^0.041  1422209^0.203  1416723^0.014  1486345^0.054  1863034^0.027  1159232^0.014  1121982^0.081  2670576^0.014  9218553^0.027  1251035^0.054  9832597^0.054  8178063^0.014  2019075^0.014  1804069^0.014  1437399^0.014  9477292^0.014  1029066^0.014  1369546^0.054  8414619^0.014  2550164^0.027  1534442^0.014  9936626^0.014  9724923^0.014  9632823^0.014  2638205^0.014  1203048^0.014  1297203^0.014  2821364^0.014  9693182^0.014  3055374^0.014  ", "fields": ["_id"]}}], "minimum_should_match": 1, "filter": null}}, "_source": ["sku", "name"], "rescore": {"window_size": 500, "query": {"rescore_query": {"sltr": {"params": {"keywords": "lcd monitor", "click_prior_query": "9346861^0.041  2596077^0.054  7662095^0.014  2815266^0.041  1422209^0.203  1416723^0.014  1486345^0.054  1863034^0.027  1159232^0.014  1121982^0.081  2670576^0.014  9218553^0.027  1251035^0.054  9832597^0.054  8178063^0.014  2019075^0.014  1804069^0.014  1437399^0.014  9477292^0.014  1029066^0.014  1369546^0.054  8414619^0.014  2550164^0.027  1534442^0.014  9936626^0.014  9724923^0.014  9632823^0.014  2638205^0.014  1203048^0.014  1297203^0.014  2821364^0.014  9693182^0.014  3055374^0.014  "}, "model": "ltr_model", "store": "week1"}}, "score_mode": "total", "query_weight": 1, "rescore_query_weight": 2}}}```