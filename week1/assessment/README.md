# Project Assessment

## 1. Do you understand the steps involved in creating and deploying an LTR model?  Name them and describe what each step does in your own words.

The steps are the following:
1) Create a featureset: decide which features to use for the LTR model. Those features can be query-dependent or independent.
2) Train and Test the model: In this step we should train and evaluate models on the featureset. We can use multiples models and objective functions for that.
3) Deploy model: Deploy the model when we find the best one.


## 2. What is a feature and featureset?

** _feature is the data or metadata related to a document or a query. and that can be used as a signal for the model.
** _featureset_ is the set of features that we use in our model. 

## 3. What is the difference between precision and recall?

- Precision determines the percentage of results in a top-k result set that are considered relevant.
- Recall is the number of relevant documents that were returned in the top-k result over the number amount of relevant documents that exist.

Precision tell us about the quality of a result rank. While Recall tells us how much the rank can be improved (the best case).

## 4. What are some of the traps associated with using click data in your model?

Click data may not be a great signal of relevance because of:
- position bias: the toppest results will have more exposure and because of that more clicks
- clicks rely on past data, we cannot guarantee if good past data remains good. 
- Clicks are not good for documents that are not being shown in past (e.g: new documents (because they can be relevant and not be shown) )

## 5. What are some of the ways we are faking our data and how would you prevent that in your application?

The impressions and clicks are based on a reverse engineering. To prevent that in a application we should log the impressions and clicks. For testing the quality of the model we can rely on an A/B testing instead of the training itself. 

## 6. What is target leakage and why is it a bad thing?

Target leakage is when the data is being shared between the training and test. Then, it can be overfitted and because of that not, do not generalize well the information and behave badly in real cases.

## 7. When can using prior history cause problems in search and LTR?

Using prior history relies on the assumption that what existed before was good. 
** A Good Result can "expire" and start to be a Bad Result. 
** A Bad Result can turn into a Good Result (for example: A new music in a musical search engine).
** New Results don't have any information and they cannot be shown or be shown more than it should be. 



## Best Result

Simple MRR is 0.399
LTR Simple MRR is 0.197
Hand tuned MRR is 0.451
LTR Hand Tuned MRR is 0.202

Simple p@10 is 0.126
LTR simple p@10 is 0.065
Hand tuned p@10 is 0.156
LTR hand tuned p@10 is 0.070
Simple better: 668 LTR_Simple Better: 369 Equal: 20
HT better: 696 LTR_HT Better: 417 Equal: 13