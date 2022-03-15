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

### What values did you achieve for P@1, R@3, and R@5? 

Number of Training examples: 100000

| min_queries | Learning Rate | Word Ngrams | Epochs | minn | maxn | P@1   | R@3   | R@5   |
|-------------|---------------|-------------|--------|------|------|-------|-------|-------|
| 25          | 0.1           | 2           | 100    |      |      | 0.533 | 0.719 | 0.783 |
| 25          | 0.1           | 2           | 200    | 4    | 8    | 0.541 | 0.723 | 0.784 |
| 25          | 0.2           | 2           | 50     |      |      | 0.534 | 0.720 | 0.783 |
| 50          | 0.5           | 2           | 25     |      |      | 0.518 | 0.697 | 0.763 |
| 50          | 0.1           | 0           | 100    |      |      | 0.534 | 0.719 | 0.783 |
| 100         |               |             |        |      |      |       |       |       |
| 500         |               |             |        |      |      |       |       |       |
| 500         |               |             |        |      |      |       |       |       |
| 1000        |               |             |        |      |      |       |       |       |
| 2000        |               |             |        |      |      |       |       |       |
| 5000        |               |             |        |      |      |       |       |       |

## For integrating query classification with search:

Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure
to include the classifier output for those queries.

Given 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some
other reason. Again, include the classifier output for those queries.

## Problems I encountered

Again, fasttext did not allow a learning rate of 1.0 ("Encountered NaN" error).