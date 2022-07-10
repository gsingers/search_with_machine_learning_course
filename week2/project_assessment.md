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

TODO

- What threshold score did you use?

0.75

- Were you able to find the additional results by matching synonyms?



4. For classifying reviews:

- What precision (P@1) were you able to achieve?

- What fastText parameters did you use?

- How did you transform the review content?

- What else did you try and learn?