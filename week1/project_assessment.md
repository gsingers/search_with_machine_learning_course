# Project Assessment

## 1. Do you understand the steps involved in creating and deploying an LTR model?  Name them and describe what each step does in your own words.

Yes!

* Create featureset: decide which features to use for the LTR model. Those can be query-dependent or independent and should be accessible. In this step, one should also collect judgements (either implictit or explicit) for the data.
* Train and test model: In this step, one should train and evaluate models on the featureset. For model tunning, one can change features and/or model(we worked with XGBoost, but there are other possible models for LTR).
* Deploy model: once there is a winner, the trained model should be deployed to the search infrastructure.

Once the model is deployed, it is a good practice to evaluate it's performance online. Usually, this happens through A/B testing.

## 2. What is a feature and featureset?
* **Feature:** some data related to the document and/or query, that can be used as a signal for the model.
* **Featureset:** one or many features put together are a featureset. A featureset is the dataset in which a model can be trained and evaluated.

## 3. What is the difference between precision and recall?

Precision relates to the fraction of relevant results among the results of a query, while recall relates to the fraction of relevant results retrieved in the result set.

So, in the search context, precision is usually related to top n results of a query and is a measure of SERP quality. Recall, on the other hand, is not easily calculated, since it's not easy to define what what how many relevant results there are for a given query query.


## 4. What are some of the traps associated with using click data in your model?

Click data may not be a great signal of relevance because of:
- position bias: documents that are presented at the top of a SERP have more exposition and, therefore, will attract more clicks, even though it isn't the most relevant result.
- in some cases, the result for the query is already shown in the SERP, so there is no need for a click.
- clicks rely on past data. The search engines could be different then, in a way that there could be more relevant documents that were never shown.

## 5. What are some of the ways we are faking our data and how would you prevent that in your application?

The impressions presented in the dataset are synthetic, based on a "reverse engineering" to infer the SERP. To prevent that in applications, one should log impressions and clicks related to queries, so there is no need to synthetize data.

## 6. What is target leakage and why is it a bad thing?

Target leakage happens when there is data available in the training process that should not be available during prediction time. This makes the model less general (since it doesn't have all the data it needed to predict things), leading to a model that performs badly when deployed.

## 7. When can using prior history cause problems in search and LTR?

Using prior history relies on the assumption that what existed before was good. However, if a very relevant document for a given query was so poorly ranked it never was shown to the user, that information is lost and the featureset will be biased towards this bad result, leading to poor models.


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
