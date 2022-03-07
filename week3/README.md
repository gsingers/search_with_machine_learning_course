Week3 Project
===
The following are the notes on the sub-tasks of W3 project.

Level 1: Classifying Product Names to Categories
===

Without prunning the infrequent category labels, the performance of the model:

Number of words:  25512
Number of labels: 1938

Test:
N       10000
P@1     0.729
R@1     0.729

With pruning the infrequent category labels, the results are like so:

| min_product | n_words | n_labels | P@1   | R@1   |
|-------------|---------|----------|-------|-------|
| 50          | 19097   | 512      | 0.752 | 0.752 |
| 100         | 16273   | 262      | 0.83  | 0.83  |
| 200         | 12770   | 113      | 0.898 | 0.898 |

I did not do the tree pruning, as I ran out of time. Intuitively it should help increase P and R, because predicting at higher levels in the product taxonomy can be easier (and less labels).

Parameters for training the models:

    ~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/output_punct_to_space_lc.fasttext_50.train -output /workspace/datasets/fasttext/full_model_fifty -loss hs -epoch 100

In particular, using hierarchical softmax instead of the regular softmax gives a significant boost to the training speed.


Level 2: Derive Synonyms from Content
===

### What 20 tokens did you use for evaluation?

*5 product types:*
- headphones
- phone
- speakers
- keyboard
- tables

*5 brands:*
- sony
- focusrite
- apple
- samsung
- lg

*5 models:*
- thinkpad
- imac
- elitebooks
- iphone
- galaxy

*5 attributes:*
- white
- camera
- resolution
- wireless
- bluetooth

### What fastText parameters did you use?
minCount of 10, 20 and 50

### How did you transform the product names?
Removed punctuation, dropped extra spaces and lowercased.
I experimented with stemming as well, but the synonyms also get stemmed, so decided to avoid this.

### What threshold score did you use? 
0.7

### What synonyms did you obtain for those tokens?
| query       | synonyms (including scores)                               |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| headphones      | earbud 0.883999, ear 0.839445, bud 0.73297, canceling 0.721314, earbuds 0.71985 |
| phone      | phones 0.759353, telephone 0.735768, answering 0.71059, speakerphone 0.709176 |
| speakers      | speaker 0.829672, woofer 0.744031, pair 0.73698, polypropylene 0.730997, cones 0.729895 |
| keyboard      | keyboards 0.896709, keys 0.729559 |
| tables      | table 0.846664, tablets 0.83013, tabletop 0.825068, tablet 0.775806 |
| sony      | NONE, but good examples below 0.7: vaio 0.597231, walkman 0.574167 |
| focusrite      | NONE |
| apple      | apple® 0.802705 |
| samsung      | lg 0.742252 |
| lg      | samsung 0.742252 |
| thinkpad      | ideapad 0.86554, ibm 0.819048, lenovo 0.815385, fujitsu 0.76064, atg 0.752287, biz 0.732815, nimh 0.719717 |
| imac      | mac 0.75241, image 0.722575 |
| elitebooks      | notebooks 0.848634, notebook 0.727201|
| iphone | iphone® 0.935992, 4s 0.780405, 3gs 0.763268 |
| galaxy | NONE |
| white | NONE |
| camera | cameras 0.791214, 2mp 0.762989, 1mp 0.746407, 0mp 0.737059, slr 0.73256, megapixel 0.729205, mp 0.725077, zoom 0.720591, nikon 0.710599, 85mm 0.701001 |
| resolution | revolution 0.911922, evolution 0.905107 |
| wireless | NONE |
| bluetooth | jabra 0.72248 |