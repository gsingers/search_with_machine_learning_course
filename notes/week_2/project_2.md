# Project 2

- smaller index
- generate training data
- running fast text
	- classification: supervised
	- synonyms: skipgrams, nearest neighbor
- integrate synonyms into search


### Document catogorisation

- get product name and category
- put into key value keys that fastText can process
- for class we are running training and testing on two different 10% samples (10,000) for speed reasons
	- we need to shuffle the data to remove artifacts from ordering
- only keep entries that are associated with a label assigned to at least 500 products. (pandas df or dictionary)
- aim for precision above 90%
- because we throw away categories we don't have much data for. We could therefore look up the hierarchy (read category XML)

### Synonyms

- product titles with labels removed
- normalization required
- build synonym set
- integrate with search
	- extract most frequent words
	- run nn and keeps pairs above a certain threshold
	- integrate to analyzer in Opensearch as synonym token filter
- [Synonyms and search](https://dtunkelang.medium.com/real-talk-about-synonyms-and-search-bb5cf41a8741)
- FastText and similar approaches return highly correlated terms but not true synonyms but these could be a filter. Query rewrites could also be taken as a synonym but it's worth having some human layer to check.
- Knowledge graphs
	- very expressive (complex)
	- quality can be patchy, one thing might have a very complete data coverage while another might not (especially crowd sourced)
	- is this complexity worth the return
- recall problem with synonyms, the synonym is frequent but returning very large result sets, or low CTR might be an indicated that the synonym is having a negative effect

The user uses a word that wouldn't have matched any results but not match a bunch of results, so they appear highly in the queries but not in the logs (as they lead to small or empty result sets) this is where they have the most impact - note this could be good or bad.

## Lemmatization versus stemming

Lemmatization is safer, same semantic form while stemming is heuristic and follows rules like removing endings, it can however work for words which are unknown. More [here](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45)




LTR pipeline:
- build a feature store in opensearch for our ranking algorithm
- add our model (XGBoost)
- use logging to evaluate our predictions for queries
- give weights to our features to improve MMR with the model

Cold start problem:
- we don't have enough logs to mine (ie new index or low volume)
- BM25 is very effective
- you need judgments that generalize to most query-document pairs



Conferences SpecialInterestGroupInformationRetrieval, KnowledgeDiscoveryD
[reinforcement learning assisted search](https://us06st1.zoom.us/web_client/4qu8baa/html/externalLinkPage.html?ref=https://medium.com/sajari/reinforcement-learning-assisted-search-ranking-a594cdc36c29)