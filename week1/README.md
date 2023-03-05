# Notes for Week 1

Install jupyter for interactive exploration of data
```bash
/home/gitpod/.pyenv/versions/3.9.7/envs/search_with_ml/bin/python3.9 -m pip install jupyter
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
# 
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

```python
features = [
            'name_match', 'name_match_phrase', 
            'customer_review_average', 'customer_review_count',
            'artist_name_match_phrase',
            'short_desc_match_phrase', 'long_desc_match_phrase',
            'sales_rank_short_term', # 'sales_rank_medium_term', 'sales_rank_long_term',
            # 'sale_price', 'on_sale'
            ]

# ./ltr-end-to-end.sh -y -m 0 -c quantiles

# Simple MRR is 0.285
# LTR Simple MRR is 0.432
# Hand tuned MRR is 0.423
# LTR Hand Tuned MRR is 0.437

# Simple p@10 is 0.119
# LTR simple p@10 is 0.161
# Hand tuned p@10 is 0.171
# LTR hand tuned p@10 is 0.176
# Simple better: 472      LTR_Simple Better: 638  Equal: 9
# HT better: 629  LTR_HT Better: 656      Equal: 7
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


```
