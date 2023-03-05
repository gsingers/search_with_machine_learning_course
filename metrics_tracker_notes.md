

```Level 1: Initial run (after step 3.a and 3.b)```
Simple MRR is 0.285
LTR Simple MRR is 0.284
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.423

Simple p@10 is 0.120
LTR simple p@10 is 0.120
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.168
Simple better: 17       LTR_Simple Better: 6    Equal: 1097
HT better: 503  LTR_HT Better: 80       Equal: 705

------------

```Level 2: By setting main-query weight as 0 and rescore as 1```
Simple MRR is 0.285
LTR Simple MRR is 0.221
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.233

Simple p@10 is 0.120
LTR simple p@10 is 0.069
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.078
Simple better: 687      LTR_Simple Better: 417  Equal: 16
HT better: 713  LTR_HT Better: 564      Equal: 11
------------

```Level 2: Feature that uses phrases on the name-field with a slop of 6```
Simple MRR is 0.285
LTR Simple MRR is 0.226
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.226

Simple p@10 is 0.120
LTR simple p@10 is 0.087
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.093
Simple better: 634      LTR_Simple Better: 465  Equal: 21
HT better: 688  LTR_HT Better: 586      Equal: 14
------------

```Level 2: Adding features - customerReviewAverage and customerReviewCount```
Simple MRR is 0.285
LTR Simple MRR is 0.361
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.366

Simple p@10 is 0.120
LTR simple p@10 is 0.145
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.158
Simple better: 501      LTR_Simple Better: 609  Equal: 10
HT better: 645  LTR_HT Better: 626      Equal: 17
------------

```Level 2: Phrase Match - artistName, shortDescription, longDescription with slop as 6```
Simple MRR is 0.285
LTR Simple MRR is 0.401
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.402

Simple p@10 is 0.120
LTR simple p@10 is 0.160
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.177
Simple better: 466      LTR_Simple Better: 645  Equal: 9
HT better: 578  LTR_HT Better: 695      Equal: 15
------------

```Level 2: Trying with salesRankShortTerm```
Simple MRR is 0.285
LTR Simple MRR is 0.443
Hand tuned MRR is 0.423
LTR Hand Tuned MRR is 0.451

Simple p@10 is 0.120
LTR simple p@10 is 0.173
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.192
Simple better: 442      LTR_Simple Better: 667  Equal: 11
HT better: 602  LTR_HT Better: 672      Equal: 14
------------