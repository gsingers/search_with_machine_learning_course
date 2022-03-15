## query classification

### How many unique categories did you see?


| min_queries | unique categories |
|-------------|-------------------|
| 25          | 1133              |
| 50          | 1016              |     
| 100         | 878               |     
| 500         | 542               |     
| 1000        | 386               |     
| 2000        | 247               |
| 5000        | 124               |

<br>

### How did you transform the queries?

#### First try 

see `transform_queries` in `create_labeled_queries`

- lowercase
- word tokenization (NLTK)
- removed stopwords and words with length < 3
- removed non-alphanumeric letters
- English Snowball stemming
- sort query words alphabetically

#### Second try 

see `transform_queries2` in `create_labeled_queries`

- lowercase
- word tokenization (NLTK)
- removed stopwords and words with length < 3
- kept only ASCII letters
- no stemming, only removing trailing s
- no sorting

I didn't see much difference between the two approaches. 

The results were equally bad :-(

### What values did you achieve for P@1, R@3, and R@5? 

Number of Training examples: 200000
Number of Testing examples: 20000

Results are with the second method of query preprocessing.

Prediction threshold: 0.8

Output of `test_model.py`

#### Min Queries: 25

R@1	0.540
R@3	0.725
R@5	0.788

Prediction for ipad 2: pcmcat209000050007
Prediction for iphone: pcmcat209400050001
Prediction for blue sunshine CD: cat02015

#### Min Queries: 50

R@1	0.554
R@3	0.744
R@5	0.812

Prediction for blue sunshine CD: cat02015

#### Min Queries: 100

R@1	0.547
R@3	0.740
R@5	0.804

Prediction for ipad 2: pcmcat209000050007
Prediction for blue sunshine CD: cat02015

#### Min Queries: 500

R@1	0.546
R@3	0.741
R@5	0.808

Prediction for ipad 2: pcmcat209000050007

#### Min Queries: 1000

R@1	0.552
R@3	0.750
R@5	0.815

Prediction for ipad 2: pcmcat209000050007
Prediction for blue sunshine CD: cat02015

#### Min Queries: 2000

R@1	0.565
R@3	0.760
R@5	0.828

Prediction for ipad 2: pcmcat209000050007
Prediction for blue sunshine CD: cat02015

#### Min Queries: 5000

R@1	0.587
R@3	0.786
R@5	0.849

Prediction for ipad 2: pcmcat209000050007
Prediction for blue sunshine CD: cat02015

## For integrating query classification with search

### Filtering

#### My threshold for filtering: 0.8

#### Filter Query

    "query": {
      "bool": {
        "filter": [
          {
            "terms": {
              "categoryPathIds": [
                "cat02015"
            ]
          }
        }...
  
### Boosting

#### My threshold for boosting: 0.3

#### Boosting Query

Q: Is this the way boosting is done? Or would a function_score be better?

    "query": {
            "bool": {
                "should": [{
                    "terms": {
                        "categoryPathIds": ["pcmcat209400050001"],
                        "boost": 20.0
              }}],...

### Good Example

Q: It seems it only works well for head queries?

Query: ipad 2
pcmcat209000050007 (category ipad) 

Query: iphone
pcmcat209400050001 ("All Mobile Phones with Plans")

Query: ear bud
pcmcat144700050004 ("All Headphones")

Query: Pokemon
abcat0707002 ("Nintendo DS Games")
Confidence: 0.47

The prediction was good but the boosting did nothing because there were no products in that category.  

### Bad Example

Query: Blue Sunshine CD
cat02015 ("Movies & TV Shows")

## Problems I encountered

Again, fasttext did not allow a learning rate of 1.0 ("Encountered NaN" error).

Fasttest did not allow concurrent training of models, apparently. When I tried to train several models at once, 
all hat the same results even though the training data was different.  

Replacing categories with parent categories hat surprisingly little effect. 