# Project Assessment

## 1. Do you understand the steps involved in creating and deploying an LTR model?  Name them and describe what each step does in your own words.


## 2. What is a feature and featureset?


## 3. What is the difference between precision and recall?


## 4. What are some of the traps associated with using click data in your model?


## 5. What are some of the ways we are faking our data and how would you prevent that in your application?


## 6. What is target leakage and why is it a bad thing?


## 7. When can using prior history cause problems in search and LTR?


## 8. Submit your project along with your best MRR scores

I have played around with many feature configurations, eventually, I settled for this - unfortunatelly, I didn't save the combinations to compare.

Running the training with this parameters increased Hand Tuned MRR for both models on most feature configurations.

```
python week1/utilities/build_ltr.py --xgb_test /workspace/ltr_output/test.csv --train_file /workspace/ltr_output/train.csv --output_dir /workspace/ltr_output --xgb_test_num_queries 100 --xgb_main_query 1 --xgb_rescore_query_weight 2 && python week1/utilities/build_ltr.py --analyze --output_dir /workspace/ltr_output 
```


Results:

````
Simple MRR is 0.293
LTR Simple MRR is 0.287
Hand tuned MRR is 0.462
LTR Hand Tuned MRR is 0.483

Simple p@10 is 0.133
LTR simple p@10 is 0.120
Hand tuned p@10 is 0.197
LTR hand tuned p@10 is 0.211
Simple better: 576      LTR_Simple Better: 375  Equal: 380
HT better: 570  LTR_HT Better: 551      Equal: 305
```
