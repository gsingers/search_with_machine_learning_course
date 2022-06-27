# Level 1

## Testing `main_query` and `rescore_query` weights:
- `main` - 1; `rescore` - 1000
```
Simple MRR is 0.283
LTR Simple MRR is 0.264
Hand tuned MRR is 0.425
LTR Hand Tuned MRR is 0.378

Simple p@10 is 0.096
LTR simple p@10 is 0.087
Hand tuned p@10 is 0.163
LTR hand tuned p@10 is 0.139
Simple better: 268      LTR_Simple Better: 136  Equal: 1377
HT better: 894  LTR_HT Better: 514      Equal: 733
```
- `main` - 1000; `rescore` - 1
```
Simple MRR is 0.306
LTR Simple MRR is 0.306
Hand tuned MRR is 0.416
LTR Hand Tuned MRR is 0.416

Simple p@10 is 0.117
LTR simple p@10 is 0.117
Hand tuned p@10 is 0.167
LTR hand tuned p@10 is 0.166
Simple better: 0        LTR_Simple Better: 0    Equal: 2095
HT better: 91   LTR_HT Better: 207      Equal: 2099
```
- `main` - 0; `rescore` - 1
```
Simple MRR is 0.334
LTR Simple MRR is 0.201
Hand tuned MRR is 0.422
LTR Hand Tuned MRR is 0.224

Simple p@10 is 0.095
LTR simple p@10 is 0.066
Hand tuned p@10 is 0.159
LTR hand tuned p@10 is 0.074
Simple better: 1018     LTR_Simple Better: 1039 Equal: 32
HT better: 1179 LTR_HT Better: 1070     Equal: 32
```

# Level 2

**end-to-end script:** `./ltr-end-to-end.sh -y -m 0 -c quantiles`

- Add a feature that uses phrases on the name field.  It should use the match_phrase query and the passed in keywords, along with a slop of 6. Our run:
```
Simple MRR is 0.331
LTR Simple MRR is 0.189
Hand tuned MRR is 0.430
LTR Hand Tuned MRR is 0.194

Simple p@10 is 0.139
LTR simple p@10 is 0.070
Hand tuned p@10 is 0.177
LTR hand tuned p@10 is 0.081
Simple better: 673      LTR_Simple Better: 599  Equal: 18
HT better: 794  LTR_HT Better: 612      Equal: 23
```

-  Add two features, one for customerReviewAverage and one for customerReviewCount.
```
Simple MRR is 0.351
LTR Simple MRR is 0.370
Hand tuned MRR is 0.453
LTR Hand Tuned MRR is 0.359

Simple p@10 is 0.111
LTR simple p@10 is 0.110
Hand tuned p@10 is 0.187
LTR hand tuned p@10 is 0.116
Simple better: 570      LTR_Simple Better: 467  Equal: 7
HT better: 665  LTR_HT Better: 495      Equal: 13
```

- add phrase match with a slop of 6 for: artistName, shortDescription, longDescription
```
Simple MRR is 0.247
LTR Simple MRR is 0.307
Hand tuned MRR is 0.422
LTR Hand Tuned MRR is 0.296

Simple p@10 is 0.072
LTR simple p@10 is 0.085
Hand tuned p@10 is 0.161
LTR hand tuned p@10 is 0.081
Simple better: 567      LTR_Simple Better: 591  Equal: 15
HT better: 712  LTR_HT Better: 538      Equal: 9
```


