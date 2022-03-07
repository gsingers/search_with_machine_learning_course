To assess your project work, you should be able to answer the following questions:

For classifying product names to categories:

- What precision (P@1) were you able to achieve? I tried a number of options and the P@1 values ranged from 0.141 to 0.919. A
- What fastText parameters did you use?
I tried min_product values of 0, 50 and 100, learning rates of 0.1 and 1, category depths of 2, 3 and maximum possible and learning epochs of 25, wordNgrams=2
- How did you transform the product names?
removed punctuation, lowercased, tokenized and Snowballed stemmed.
- How did you prune infrequent category labels, and how did that affect your precision?
I tried 50 and 100. In general, more pruning led to better P@1 but, (I guess) lower product coverage.
- How did you prune the category tree, and how did that affect your precision?
I tried depths of 2 and 3 as well as the default of maximum. The deeper, the finer grain the categorization and the lower the P@1
 
For deriving synonyms from content:

- What 20 tokens did you use for evaluation?
Product: laptop, tv, monitor, phon, camera
Brands: soni, assus, lenovo, samsung, apple
Models: ipad, iphon, netbook, xbox
Attributes: silver, black, wide, mobile, fast
- What fastText parameters did you use?
minCount 10, 15, lr = 0.1 and 0.3, epoch=25
- How did you transform the product names?
similar to category names
- What threshold score did you use?
I just did a quick sanity check. Part of the challenge I had was that the stemming and tokenization of the data meant that sometimes using the original words did not yield results. For example Sony became soni.
- What synonyms did you obtain for those tokens?

- For integrating synonyms with search: TBD
- How did you transform the product names (if different than previously)?
- What threshold score did you use?
- Were you able to find the additional results by matching synonyms?

For classifying reviews: TBD (continuing)
- What precision (P@1) were you able to achieve?
- What fastText parameters did you use?
- How did you transform the review content?
- What else did you try and learn?