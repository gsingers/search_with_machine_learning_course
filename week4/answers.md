## query classification

How many unique categories did you see in your rolled up training data when you set the minimum number of queries per
category to 100? To 1000?


| min_queries | unique categories |
|-------------|-------------------|
| 50          | 1016              |     
| 100         | 878               |     
| 500         | 542               |     
| 1000        | 386               |     

<br>

What values did you achieve for P@1, R@3, and R@5? You should have tried at least a few different models, varying the
minimum number of queries per category as well as trying different fastText parameters or query normalization. Report at
least 3 of your runs.

| Learning Rate | Word Ngrams | Epochs | min_queries | P@1   | R@3   | R@5   |
|---------------|-------------|--------|-------------|-------|-------|-------|
| 0.5           | 2           | 25     | 50          | 0.518 | 0.697 | 0.763 |
| 0.7           | 3           | 50     |             |       |       |       |
|               |             |        |             |       |       |       |

## For integrating query classification with search:

Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure
to include the classifier output for those queries.

Given 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some
other reason. Again, include the classifier output for those queries.

## Problems I encountered

Again, fasttext did not allow a learning rate of 1.0 ("Encountered NaN" error).