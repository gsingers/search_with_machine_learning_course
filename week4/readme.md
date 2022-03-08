# Week 4

## Setup
pyenv activate search_with_ml_week4
alias fasttext=~/fastText-0.9.2/fasttext
pip install ipython numpy pandas nltk fasttext

## Level 1 - Query Classification

### Task 1: Prune the category taxonomy.
$ python week4/create_labeled_queries.py --min_queries=1 --output=/workspace/datasets/labeled_query_data.txt
> categories found = 1444

$ cat /workspace/datasets/labeled_query_data.txt | wc -l 1854987
> 1854987

$ python week4/create_labeled_queries.py --min_queries=100 --output=/workspace/datasets/labeled_query_data_100.txt
> categories found = 878

$ cat /workspace/datasets/labeled_query_data_100.txt | wc -l
> 1854452

$ python week4/create_labeled_queries.py --min_queries=1000 --output=/workspace/datasets/labeled_query_data_1000.txt
> categories found = 388

$ cat /workspace/datasets/labeled_query_data_1000.txt | wc -l
> 1850373

$ python week4/create_labeled_queries.py --min_queries=10000 --output=/workspace/datasets/labeled_query_data_10000.txt
> categories found = 70

$ cat /workspace/datasets/labeled_query_data_10000.txt | wc -l
> 1781690


### Task 2: Train a query classifier.

### min_queries=1

shuf < /workspace/datasets/labeled_query_data.txt > /workspace/datasets/labeled_query_data.txt.rand
head -n 50000 /workspace/datasets/labeled_query_data.txt.rand > /workspace/datasets/labeled_query_data.txt.train
tail -n 50000 /workspace/datasets/labeled_query_data.txt.rand > /workspace/datasets/labeled_query_data.txt.test


fasttext supervised -input /workspace/datasets/labeled_query_data.txt.train -output queres -loss hs

fasttext test queres.bin /workspace/datasets/labeled_query_data.txt.test 1

N       49835
P@1     0.471
R@1     0.471

N       49835
P@3     0.208
R@3     0.623

N       49835
P@5     0.136
R@5     0.68

fasttext supervised -input /workspace/datasets/labeled_query_data.txt.train -output queres -loss hs -lr 0.3 -epoch 20 -wordNgrams 2

N       49835
P@1     0.507
R@1     0.507

N       49835
P@3     0.226
R@3     0.677

N       49835
P@5     0.147
R@5     0.736


### min_queries=100


shuf < /workspace/datasets/labeled_query_data_100.txt > /workspace/datasets/labeled_query_data_100.txt.rand
head -n 50000 /workspace/datasets/labeled_query_data_100.txt.rand > /workspace/datasets/labeled_query_data_100.txt.train
tail -n 50000 /workspace/datasets/labeled_query_data_100.txt.rand > /workspace/datasets/labeled_query_data_100.txt.test


fasttext supervised -input /workspace/datasets/labeled_query_data_100.txt.train -output queres -loss hs -lr 0.3 -epoch 20 -wordNgrams 2

fasttext test queres.bin /workspace/datasets/labeled_query_data_100.txt.test 1

N       49991
P@1     0.507
R@1     0.507

N       49991
P@3     0.225
R@3     0.674

N       49991
P@5     0.147
R@5     0.735

### min_queries=1000


shuf < /workspace/datasets/labeled_query_data_1000.txt > /workspace/datasets/labeled_query_data_1000.txt.rand
head -n 50000 /workspace/datasets/labeled_query_data_1000.txt.rand > /workspace/datasets/labeled_query_data_1000.txt.train
tail -n 50000 /workspace/datasets/labeled_query_data_1000.txt.rand > /workspace/datasets/labeled_query_data_1000.txt.test


fasttext supervised -input /workspace/datasets/labeled_query_data_1000.txt.train -output queres -loss hs -lr 0.3 -epoch 20 -wordNgrams 2

fasttext test queres.bin /workspace/datasets/labeled_query_data_1000.txt.test 1

N       50000
P@1     0.503
R@1     0.503

N       50000
P@3     0.228
R@3     0.684

N       50000
P@5     0.149
R@5     0.745


fasttext supervised -input /workspace/datasets/labeled_query_data_1000.txt.train -output queres -loss hs -lr 0.3 -epoch 200 -wordNgrams 2

fasttext test queres.bin /workspace/datasets/labeled_query_data_1000.txt.test 1

N       50000
P@1     0.503
R@1     0.503

N       50000
P@3     0.226
R@3     0.679

N       50000
P@5     0.148
R@5     0.737

fasttext supervised -input /workspace/datasets/labeled_query_data_1000.txt.train -output queres -loss hs -lr 0.3 -epoch 20 -wordNgrams 2 -minCount 100

fasttext test queres.bin /workspace/datasets/labeled_query_data_1000.txt.test 1

N       50000
P@1     0.499
R@1     0.499

N       50000
P@3     0.224
R@3     0.671

N       50000
P@5     0.147
R@5     0.733



fasttext supervised -input /workspace/datasets/labeled_query_data_1000.txt.train -output queres -loss hs -lr 0.3 -epoch 20 -minCount 100
fasttext test queres.bin /workspace/datasets/labeled_query_data_1000.txt.test 1

N       50000
P@1     0.195
R@1     0.195

N       50000
P@3     0.0754
R@3     0.226

N       50000
P@5     0.061
R@5     0.254



fasttext supervised -input /workspace/datasets/labeled_query_data_1000.txt.train -output queres -loss hs -epoch 20 -minCount 100

fasttext test queres.bin /workspace/datasets/labeled_query_data_1000.txt.test 1

N       50000
P@1     0.329
R@1     0.329

N       50000
P@3     0.157
R@3     0.47

N       50000
P@5     0.107
R@5     0.537


fasttext supervised -input /workspace/datasets/labeled_query_data_1000.txt.train -output queres -epoch 20 -minCount 100

fasttext test queres.bin /workspace/datasets/labeled_query_data_1000.txt.test 1




### min_queries=10000


shuf < /workspace/datasets/labeled_query_data_10000.txt > /workspace/datasets/labeled_query_data_10000.txt.rand
head -n 50000 /workspace/datasets/labeled_query_data_10000.txt.rand > /workspace/datasets/labeled_query_data_10000.txt.train
tail -n 50000 /workspace/datasets/labeled_query_data_10000.txt.rand > /workspace/datasets/labeled_query_data_10000.txt.test


fasttext supervised -input /workspace/datasets/labeled_query_data_10000.txt.train -output queres -loss hs -lr 0.3 -epoch 20 -wordNgrams 2

fasttext test queres.bin /workspace/datasets/labeled_query_data_10000.txt.test 1

N       50000
P@1     0.578
R@1     0.578

N       50000
P@3     0.257
R@3     0.771

N       50000
P@5     0.166
R@5     0.832





# Project Assessment

To assess your project work, you should be able to answer the following questions:

## For query classification:
-  How many unique categories did you see in your rolled up training data when you set the minimum number of queries per category to 100? To 1000?

    100: categories found = 878
    1000: categories found = 388

- What values did you achieve for P@1, R@3, and R@5? You should have tried at least a few different models, varying the minimum number of queries per category as well as trying different fastText parameters or query normalization. Report at least 3 of your runs.



- For integrating query classification with search:

Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure to include the classifier output for those queries.

Given 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some other reason. Again, include the classifier output for those queries.