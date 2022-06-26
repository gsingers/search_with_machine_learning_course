1. Do you understand the steps involved in creating and deploying an LTR model?  Name them and describe what each step does in your own words.
- Initialize LTR storage : Tell Opensearch to use LTR
- Build LTR feature store : Identify features to use for training
- Collect judgements : Get implicit/expilcit ratings for query,document pairs
- Log the feature scores : Combine judgments and features
- Train and test the model
- Deploy the trained model to OpenSearch
- Use the trained model to search with LTR

2. What is a feature and featureset?
Feature is any signal that can help identify if a document is relevant to a query. A set of such features is a featureset.

3. What is the difference between precision and recall?
Precision - Measure of how many relevant documents are retrieved out of all the retrieved documents
Recall - Measure of how many relecant documents are retrieved out of all the relevant documents

4. What are some of the traps associated with using click data in your model?
Clicks data has factors other than relevancy included such as desirability, position bias, presentation bias etc. 

5. What are some of the ways we are faking our data and how would you prevent that in your application?
Since we don't have impressions, we're trying to build the bestbuy data presented to the user from clicks by assuming the distribution of clicked items to be similar to the position they were displayed at. 
In real life applications, this data can be logged directly from the system instead.

6. What is target leakage and why is it a bad thing?
Target leakage happens when a feature that's not going to be available during prediction is used to train the model. This results in the model overfitting on the training data.

7. When can using prior history cause problems in search and LTR?
It would cause problems if there's change in user behavior due to sales or seasonality. It could also lead to inconsistency if there's a change in the catalog or site navigation. 

8. Best scores:

Simple MRR is 0.317
LTR Simple MRR is 0.426
Hand tuned MRR is 0.386
LTR Hand Tuned MRR is 0.434

Simple p@10 is 0.114
LTR simple p@10 is 0.181
Hand tuned p@10 is 0.167
LTR hand tuned p@10 is 0.181
Simple better: 402      LTR_Simple Better: 538  Equal: 12
HT better: 511  LTR_HT Better: 567      Equal: 18