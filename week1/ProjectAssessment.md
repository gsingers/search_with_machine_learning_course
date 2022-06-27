1. Do you understand the steps involved in creating and deploying an LTR model?  Name them and describe what each step does in your own words.

It follows a four step process like any other machine learning algorithm:
* Feature Extraction - It requires we setup a Learn to Rank (LTR) storage and determine the features of the document set in question (looking for query-independent feature) for the model and, what features that need to be involved with the query as it relates to the fields in the document set. It invovles creating a training, validation and testing datasets that includes the queries, document ids, scores for each of these features as well as the relevancy score that is the target.
* Model Training: Train a model on the training data using XGBoost or RankLib and evaluate with our validation and testing data.
* Deployment: Export the best performing LTR model using the LTR plugin within ElasticSearch/OpenSearch.
* Re-Evaluation: Gather new data after the model is deployed after some time and re-evaluate for improvements.

2. What is a feature and featureset?
* A feature is a dimension of a data point that are its attributes. In the case of a search document, the title is a feature of the document.
* A featureset is all attributes that describe that data point or document.
Determining what feature to use is important in determining search relevancy and building ML models for search.

3. What is the difference between Precision and Recall.
* Precision can be described as the percentage of "relevant" documents that are returned divided by the total number of documents returned i.e TP/(TP + FP)
* Recall can be described as the percentage of "relevant" documents that are returned divided by the total number of relevant documents in the index i.e TP/(TP + FN)

4. What are some of the traps associated with using click data in your model?
They are few items for consideration when using click data for ML models:
* The presence of bot activity in search can bias certain documents to the top of the result set that is not reflective of actual user behaviour.
* Click/Impressions should have a time decay on their weight to account for change in user preference over time i.e seasonality of products such as winter clothing.
* The average user tends to not go past the first page of results with approximate 60% of the impressions can be found on the first page. This can bias relevancy of products that are relevant and should be seen not be visible to the user's natural search patterns.
* Collection of impressions and clicks for an initial with no cold start data is time consuming. Focus during that time of collection should be around base relevancy improvements.

5. What are some of the ways we are faking our data and how would you prevent that in your application?
* We are faking the aspects of a users clicking on an item as positive impressions and users not clicking on items as negative impressions. This is done in a programmatic manner and can bias your model to a point it does not function well compared to real user behaviour. In my experience, impressions are usually collected by a middle layer or proxy that checks for any anomalous activity such as botting. Also, impressions are session based to check if a user is trying to artificically increase relevancy of certain documents to the top and if it is a bad actor, those impressions can be discarded.

6. What is target leakage and why it is bad thing?
Target leakage is the use of features or information in the model training that is not expected to be at prediction/inference time. This causes the model to overestimate the performance and generally results in poor performance in produciton environments.

7. When can using prior history causes problems in search and LTR?
This usually causes issues when documents are seasonal in nature and it must be accounted for. Prior history is just a snapshot of past user behaviour and is not indicative of future user behaviour. 

8. Submit your project along with your best MRR Scores

| | |
|---:|----|
Simple MRR is | 0.270
LTR Simple MRR is | 0.443
Hand tuned MRR is | 0.414
LTR Hand Tuned MRR is | 0.415

Simple p@10 is | 0.091
LTR simple p@10 is | 0.182
Hand tuned p@10 is | 0.158
LTR hand tuned p@10 is | 0.177
Simple better: 361      LTR_Simple Better: 585        Equal: 10
HT better: 494  LTR_HT Better: 568      Equal: 18