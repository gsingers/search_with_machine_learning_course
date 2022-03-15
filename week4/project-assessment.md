# Project Assessment

To assess your project work, you should be able to answer the following questions:

For query classification:

* How many unique categories did you see in your rolled up training data when you set the minimum number of queries per category to 100? To 1000?
  - # of Categories after pruning for min # of queries per category set to 100  : 878
  - # of Categories after pruning for min # of queries per category set to 1000 : 386

* What values did you achieve for P@1, R@3, and R@5? You should have tried at least a few different models, varying the minimum number of queries per category as well as trying different fastText parameters or query normalization. Report at least 3 of your runs.

50K samples for train & 50K samples for test

    Fasttext params with 1000 as min.# of queries per category
    N: 50000 P@1: 0.470 R@3: 0.636 R@5: 0.694

    Fasttext optimized params with 1000 as min.# of queries per category
    N: 50000 P@1: 0.519 R@3: 0.705 R@5: 0.770

    Fasttext default params with 100 as min.# of queries per category
    N: 49987 P@1: 0.461 R@3: 0.614 R@5: 0.676
    
    Fasttext optimized params with 100 as min.# of queries per category
    N: 49978 P@1: 0.511 R@3: 0.695 R@5: 0.755 


For integrating query classification with search:

* Give 2 or 3 examples of queries where you saw a dramatic positive change in the results because of filtering. Make sure to include the classifier output for those queries.

- Query joystick returned 12 hits. Your query categorization model predicted: ['abcat0515020'] (Computers)
- Query samsung phone returned 551 hits. Your query categorization model predicted: ['pcmcat209400050001', 'pcmcat201900050009'] (Digital Communication and Accessories)


Given 2 or 3 examples of queries where filtering hurt the results, either because the classifier was wrong or for some other reason. Again, include the classifier output for those queries.

robots gives 2236 hits. Your query categorization model predicted: ['abcat0101001', 'pcmcat247400050000', 'cat02015', 'pcmcat209400050001', 'pcmcat209000050008']
jazz gives 10000 hits. Your query categorization model predicted: ['abcat0101001', 'pcmcat247400050000', 'cat02015', 'pcmcat209400050001', 'pcmcat209000050008']
