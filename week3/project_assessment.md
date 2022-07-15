1. For query classification:

- How many unique categories did you see in your rolled up training data when you set the minimum number of queries per category to 1000? To 10000?
```
df_1000['category'].value_counts()
cat02015              177638
abcat0101001           80213
pcmcat247400050000     79245
pcmcat209000050008     74258
pcmcat144700050004     43991
                       ...  
abcat0205003            1020
abcat0205001            1017
abcat0902001            1012
pcmcat158900050019      1008
abcat0307017            1007
Name: category, Length: 298, dtype: int64

df_10000['category'].value_counts()
cat02015              177638
abcat0101001           80213
pcmcat247400050000     79245
pcmcat209000050008     74258
pcmcat144700050004     43991
pcmcat209400050001     39682
abcat0703002           29809
pcmcat247400050001     27458
abcat0201011           25807
pcmcat209000050007     25132
pcmcat171900050029     22845
cat02009               22347
abcat0401004           20695
cat09000               18710
pcmcat232900050017     17254
abcat0208011           14857
abcat0503002           14718
abcat0302013           14398
abcat0701001           13830
pcmcat193100050014     13826
pcmcat167300050040     13682
pcmcat174700050005     13659
pcmcat214700050000     13161
pcmcat180400050000     11814
abcat0706002           10517
abcat0703001           10400
abcat0301014           10387
pcmcat164200050013     10187
pcmcat186100050006     10051
Name: category, Length: 29, dtype: int64
```


- What were the best values you achieved for R@1, R@3, and R@5? You should have tried at least a few different models, varying the minimum number of queries per category, as well as trying different fastText parameters or query normalization. Report at least 2 of your runs.

1k queries/cat, normalized queries, no stem
| Metric | Score |
|---:|---|
P@1 | 0.365
R@1 | 0.365
--  | --
P@3 | 0.16
R@3 | 0.481
--  | --
P@5 | 0.105
R@5 | 0.524

10k queries/cat, normalized queries, no stem
| Metric | Score |
|---:|---|
P@1 | 0.767
R@1 | 0.767
--  | --
P@3 | 0.306
R@3 | 0.919
--  | --
P@5 | 0.191
R@5 | 0.953

2. For integrating query classification with search:

**Query used**
```
{"size": 10, "sort": [{"_score": {"order": "desc"}}], "query": {"function_score": {"query": {"bool": {"must": [], "should": [{"match": {"name": {"query": "tv", "fuzziness": "1", "prefix_length": 2, "boost": 0.01}}}, {"match_phrase": {"name.hyphens": {"query": "tv", "slop": 1, "boost": 50}}}, {"multi_match": {"query": "tv", "type": "phrase", "slop": "6", "minimum_should_match": "2<75%", "fields": ["name^10", "name.hyphens^10", "shortDescription^5", "longDescription^5", "department^0.5", "sku", "manufacturer", "features", "categoryPath", "name_synonyms"]}}, {"terms": {"sku": ["tv"], "boost": 50.0}}, {"match": {"name.hyphens": {"query": "tv", "operator": "OR", "minimum_should_match": "2<75%"}}}], "minimum_should_match": 1, "filter": {"match": {"categoryPathIds": "abcat0101001"}}}}, "boost_mode": "multiply", "score_mode": "sum", "functions": [{"filter": {"exists": {"field": "salesRankShortTerm"}}, "gauss": {"salesRankShortTerm": {"origin": "1.0", "scale": "100"}}}, {"filter": {"exists": {"field": "salesRankMediumTerm"}}, "gauss": {"salesRankMediumTerm": {"origin": "1.0", "scale": "1000"}}}, {"filter": {"exists": {"field": "salesRankLongTerm"}}, "gauss": {"salesRankLongTerm": {"origin": "1.0", "scale": "1000"}}}, {"script_score": {"script": "0.0001"}}]}}, "_source": ["name", "shortDescription"]}
```

- Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure to include the classifier output for those queries.

| Query | # Results w/o category filter | # Results w/ category filter | Classifier output
|---:|---|---|
tv | 10000 | 2143 | abcat0101001 - All Flat-Panel TVs
phone | 9966 | 478 | pcmcat209400050001 - All Mobile Phones with Plans

- Give 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some other reason. Again, include the classifier output for those queries.

| Query | # Results w/o category filter | # Results w/ category filter | Classifier output
|---:|---|---|
earbuds | 1205 | 0 | cat02015 - Movies & TV Shows
nespresso | 8 | 0 | cat02015 - Movies & TV Shows
nintendo | 4568 | 4568 | null
