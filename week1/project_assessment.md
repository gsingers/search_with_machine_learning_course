1. Do you understand the steps involved in creating and deploying an LTR model?  Name them and describe what each step does in your own words.

Yes! The steps to creating and deploying an LTR model are:
* Feature extraction: Setup your LTR storage and determine the features from each document that you want to use as part of the LTR model (query-independent features) and which features you want that involve how the text in the query relates to the fields in each document. Create a training dataset containing queries, documents and scores for each of these features along with a relevancy score (grade) that is the target.
* Model training: Train a model on this data (XGBoost or Ranklib are common) to predict these grades given the features and test on a set of the data withheld from the model.
* Deploy the model: Export the best performing model to be used by the LTR plugin within {Open/Elastic}Search

2. What is a feature and featureset?

A feature is some piece of data about a thing that can be used by a model to determine something else about that thing. In the case of search, these things are user queries and documents that the user may want and the something else is relevancy of a document to the query.

A featureset, as the name implies, is a set of several features which relate to the same instance of a thing. For search, this would be several features related to single search and the documents of potential interest at that moment of time.

3. What is the difference between precision and recall?

Precision is the fraction of the number of positive data samples selected divided by the total number of data samples selected from the population. For search, this is the number of relevant documents retrieved divided by the total number of documents retrieved.

Recall is the fraction of the number of positive data samples selected divided by the total number of positive data samples in the population. For search, this is the number of relevant documents retrieved divided by the total number of relevant documents in the index.

4. What are some of the traps associated with using click data in your model?

Some of the traps associated with using click data are that since clicks depend on the user, they are naturally biased by the user interface with the search results. This leads to things like position and presentation biases where uses are more likely to click something just because its higher on the page or more prevalent on the page than just because its more relevant. Some cases of presentation bias are when there's things like snippets or sponsored products on SERPs which encourage users to click on that instead of other results.

Another challenge with click data is that it requires clicks! This isn't a big issue if you have lots of users on your site already, but if you're not that lucky then a click model won't work well.

5. What are some of the ways we are faking our data and how would you prevent that in your application?

In this work we are faking impressions, which are cases when users saw a product on a SERP but didn't buy it. These are negative signals that are immensely valuable to training, so in thew absence of actual impressions we've synthesized some based on what our index would return, however this is unlikely to match what the users actually saw on BestBuy's website.

6. What is target leakage and why is it a bad thing?

Target leakage is when you have data that you're using to test the performance of your model on in the training dataset. This means that if your model is trained correctly, it should know this data already and its easy for it to get correct, giving the impression that the model is performing better than it actually would with real, unseen data.

7. When can using prior history cause problems in search and LTR?

As the name says, prior history data is historical so it means that the world it came from is not the world the query is being run in. While in most cases this is not a problem, some products may change over time and become more or less popular. This may result in a product being ranked too high or low given its current popularity.

8. Submit your project along with your best MRR scores

| | |
|---:|---|
Simple MRR is  | 0.277
LTR Simple MRR is | 0.312
Hand tuned MRR is | 0.387
LTR Hand Tuned MRR is | 0.300
||
Simple p@10 is | 0.100
LTR simple p@10 is | 0.132
Hand tuned p@10 is | 0.151
LTR hand tuned p@10 is | 0.136

Simple better: 546      LTR_Simple Better: 551  Equal: 19

HT better: 641  LTR_HT Better: 588      Equal: 8