## For classifying product names to categories:

* What precision (P@1) were you able to achieve?

   ```
   (search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext supervised -epoch 10 -lr 1.0 -minCount 20  -input /workspace/datasets/fasttext/normalized_pruned_training.txt -output best_model
Read 0M words
Number of words:  505
Number of labels: 29
Progress: 100.0% words/sec/thread:   20588 lr:  0.000000 avg.loss:  0.184701 ETA:   0h 0m 0s
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext supervised -epoch 10 -lr 1.0 -minCount 20  -input /workspace/datasets/fasttext/normalized_pruned_training.t^C
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test best_model.bin /workspace/datasets/fasttext/normalized_pruned_test.txt
N       8473
P@1     0.958
R@1     0.958
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext supervised -epoch 10 -lr 1.0 -minCount 20 -wordNgrams 2 -input /workspace/datasets/fasttext/normalized_pruned_training.txt -output best_model
Read 0M words
Number of words:  505
Number of labels: 29
Progress: 100.0% words/sec/thread:    8884 lr:  0.000000 avg.loss:  0.071863 ETA:   0h 0m 0s
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test best_model.bin /workspace/datasets/fasttext/normalized_pruned_test.txt
N       8473
P@1     0.964
R@1     0.964
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext supervised -epoch 20 -lr 0.05 -minCount 20  -input /workspace/datasets/fasttext/normalized_pruned_training.txt -output best_model
Read 0M words
Number of words:  505
Number of labels: 29
Progress: 100.0% words/sec/thread:   11368 lr:  0.000000 avg.loss:  0.272522 ETA:   0h 0m 0s
(search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext test best_model.bin /workspace/datasets/fasttext/normalized_pruned_test.txt
N       8473
P@1     0.955
R@1     0.955

   ```

* What fastText parameters did you use?

   ```
    epoch: 10
    lr: 1.0
    minCount: 20
    wordNgrams : 2
   ```

* How did you transform the product names?

   normalized text

* How did you prune infrequent category labels, and how did that affect your precision?

   Applying or pruning categories with less than 500 products. It increased the precision

* How did you prune the category tree, and how did that affect your precision?
   Not done yet(Optional)

## For deriving synonyms from content:

* What were the results for your best model in the tokens used for evaluation?

   ```
   (search_with_ml) gitpod /workspace/search_with_machine_learning_course (main) $ ~/fastText-0.9.2/fasttext nn /workspace/datasets/fasttext/title_model.bin
Query word? iphone
4s 0.879192
3gs 0.803681
apple 0.787931
ipadÂ 0.731209
ipodÂ 0.727238
ipod 0.715334
ozone 0.715014
ifrogz 0.711818
fabshell 0.711245
appleÂ 0.70454
Query word? earbuds
yurbuds 0.930673
buds 0.917282
gumy 0.896624
earbud 0.851685
tunebuds 0.847586
smokin 0.827594
armband 0.805827
iclear 0.797333
aerosport 0.796391
skullcandy 0.793837
Query word? earbud
headphones 0.904032
earbuds 0.851685
ear 0.835282
headphone 0.830723
earphones 0.788251
bud 0.778444
yurbuds 0.776367
skullcandy 0.742491
buds 0.733463
gumy 0.731738
Query word? nespresso
espresso 0.985132
capresso 0.926864
espressione 0.880406
cappuccino 0.794749
gaggia 0.777042
lavazza 0.74162
mattress 0.741053
bialetti 0.73768
stovetop 0.736918
saeco 0.728312
Query word? projector
projectors 0.944411
projecta 0.92691
projects 0.890841
project 0.884441
projection 0.79548
dlp 0.786502
xga 0.781721
wxga 0.77562
3lcd 0.758655
dmd 0.758449
Query word? usb
greendrive 0.702484
simpledrive 0.696457
microdrive 0.690065
traveldrive 0.684403
jumpdrive 0.683217
twistturn 0.68312
firewire 0.679997
esata 0.677436
surfdrive 0.676549
snowdrive 0.676273
Query word?
   ```

* What fastText parameters did you use?

   ```
    -minCount 5 -epoch 5 -wordNgrams 2
   ```

* How did you transform the product names?

   Usual lowercase and normalization

## For integrating synonyms with search:

* How did you transform the product names (if different than previously)?

   Same as before

* What threshold score did you use?

   0.7

* Were you able to find the additional results by matching synonyms?

   Yes

## For classifying reviews:

What precision (P@1) were you able to achieve?

What fastText parameters did you use?

How did you transform the review content?

What else did you try and learn?
