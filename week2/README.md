## Changes from Week 1

- A new `conf` folder for capturing project specific configurations. See `week2/conf`
- Added a new analyzer to better process tokens and mixed case product names (e.g. X-Men, iPad). See the  index settings and mappings in `week2/conf/bbuy_products.json`. 
  - The [char_group tokenizer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-chargroup-tokenizer.html) breaks text into terms whenever it encounters a character which is in a defined set. It is mostly useful for cases where a simple custom tokenization is desired, and the overhead of use of the pattern tokenizer is not acceptable.
  - [Word Delimiter Graph Token Filter](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-word-delimiter-graph-tokenfilter.html) - Splits tokens at non-alphanumeric characters. The word_delimiter_graph filter also performs optional token normalization based on a set of rules. By default, the filter uses the following rules:
    - Split tokens at non-alphanumeric characters. The filter uses these characters as delimiters. For example: Super-Duper → Super, Duper
    - Remove leading or trailing delimiters from each token. For example: XL---42+'Autocoder' → XL, 42, Autocoder
    - Split tokens at letter case transitions. For example: PowerShot → Power, Shot
    - Split tokens at letter-number transitions. For example: XL500 → XL, 500
    - Remove the English possessive ('s) from the end of each token. For example: Neil's → Neil
    
    
## Tricks

- Activate the specific environment. Install jupyter & jupyterlab `pip install jupyter jupyterlab`. `jupyter-lab --NotebookApp.allow_origin='*'`. Access the jupyterlab ui at `https:///8888-gitpod-url`
- With respect to "standardizing" (or "normalizing" or "scaling") LTR features, trees-based models such standardization is not necessary as the model learns the value splits regardless. XGBoost is just finding the splits.

## Self Assessment Questionnaire

1. Do you understand the steps involved in creating and deploying an LTR model? Name them and describe what each step does in your own words.
  - Yes. Following are the steps involved.
  - Create an LTR store
  - Upload the features that we defined in conf/ltr_featureset.json. These feature sets are based off the attributes of the index containing query dependent features(name_match) and query independent features(salesShortTermRank). 
  - Create training and test datasets from click impressions by splitting on dates. We get training data before a date and test data after that date. This allows us to use prior clicks in base retrieval and the model.
  - Create the impressions data by adding impressions to approximate the Best Buy search when the data was captured. Impressions are candiate queries along with the simulated ranks, # of impressions, # of clicks. It contains both positive (containing relevant) and negative(non-relevant) sets.
  - Feature Extraction - Given the impressions file, it loops over each impression, issue query to OpenSearch using SLTR EXT function to extract the LTR features. It also adds grade based on the click models either heurisitc or ctr. It optionally performs downsampling to create a balanced training set. This outputs an SVM formatted output file containing these columns ['query', 'sku', 'clicks', 'rank', 'num_impressions', 
       'doc_id', 'product_name', 'query_id', 'name_match', 'name_phrase_match',
       'name_hyphens_min_df', 'salePrice', 'regularPrice',
       'salesRankShortTerm', 'salesRankMediumTerm', 'salesRankLongTerm',
       'click_prior', 'grade']
- Train the XGB model using the above dataset with SVM formatted output file for number of rounds with the xgb conf specified.
- Upload the model to the LTR store
- Run a sample of test queries with various query objects(simple, hand-tuned, simple with rescore enabled, hand-tuned with rescore enabled)
- Finally analyze the results with measures such as MRR, Precision. etc

2. What is feature and featureset?
  - Feature is something that can contribute to the relevance of a document to a query. This can be query independent obtained from result fields such as sales rank, sale price, regular price or document length derived indirectly or query dependent such as number of query tokens matching a doc field such as title or description or bm25 score. 

  - Feature set [1] is a set of features grouped together for logging & model evaluation. This is used to log multiple feature values for offline training and also to create a model from feature set, copying the feature set into model.

3. What is the difference between precision and recall?
  - Precision is the fraction of retrieved results that are relevant where as Recall is the fraction of relevant documents that were retrieved.
  - Precision works best with explicit judgements 
  - Recall matters heaviliy when the cost of missing a relevant result is expensive such as research & eDiscovery where as Precision matters heavily on consumer applications such as ecommerce. 
 
4. What are some of the traps associated with using click data in your model?
  - This may lead to presentation bias as only the docs shown were clicked by the user.
  - Clicks does not always convey the utility of the document for the user task in mind.
  - Not all clicks are equals. Clicks performed a year back is less important than the clicks performed a day back.

5. What are some of the ways we are faking our data and how would you prevent that in your application?
  - We are faking our impressions data of both clicked and unclicked documents. This is done by replaying the click data and 1) running a base retrieval and 2) sort by number of clicks per query.
  - In actual application, we should log the actual impressions data. 

6. What is target leakage and why is it a bad thing?
  - Target Leakage is the inclusion of columns that is duplicate of labels, labels, or tthe proxy of labels. The model can use this information during offline training and can overestimate the model confidence but the same information may not be available during te prediction time. The problem is harder to detect and can fail silently.   

7. When can using prior history cause problems in search and LTR?
  - We need to careful in choosing the data for training due to target leakage.
  - When newer documents are added to the index, newer documents will never get  a chance since we are predicting based on old documents that accrued clicks.
  - Popular documents always staying at the top.

8. Submit your project along with your best MRR Scores

Simple MRR is 0.257
LTR Simple MRR is 0.649
Hand tuned MRR is 0.409
LTR Hand Tuned MRR is 0.691

Simple p@10 is 0.095
LTR simple p@10 is 0.249
Hand tuned p@10 is 0.171
LTR hand tuned p@10 is 0.259
Simple better: 865      LTR_Simple Better: 1224 Equal: 23
HT better: 1150 LTR_HT Better: 1228     Equal: 33
 


[1] [Feature and feature sets](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/building-features.html#adding-to-an-existing-feature-set)

----
## Notes
-  The modeling is built on us creating a synthetic dataset of impressions since the original dataset does not capture the three key things we outlined above when it comes to click data. 
- We are going to do this via one of two mechanisms that you will try: 
  1) by running our queries through a “baseline retrieval” that will collect a full set of impressions (e.g. the results a user would have seen if they were using this engine) and overlaying them with our clicks or 
  2) by inferring the ranking based off the distribution of clicks and relying on position bias in our favor. 
- In essence, we are replaying our click logs from the user to gather the full list of items viewed so that we can properly log items that were clicked and not clicked. 


    # Impressions are candidate queries with *simulated* ranks added to them as well as things like number of impressions
    # and click counts.  Impressions are what we use to then generate training data.  In the real world, you wouldn't
    # need to do this because you would be logging both clicked and unclicked events.
    # TLDR: we are trying to build a dataset that approximates what Best Buy search looked like back when this data was captured.
    # We have two approaches to impressions:
    # 1) We synthesize/infer them from the existing clicks, essentially assuming there is a built in position bias in the logs that *roughly* approximates the actual ranking of Best Buy search
    #    back when this data was captured.  Run using --generate_impressions and --synthesize
    # 2) Taking --generate_num_rows, run a random sample of queries through our current search engine.  If we find docs that have clicks, mark them as relevant.  All else are non-relevant.
    # Both approaches add rank, clicks and num_impressions onto the resulting data frame
    # We also dump out a map of queries to query ids.  Query ids are used in our XGB model.
    # Outputs to --output_dir using the --impressions_file argument, which defaults to impressions.csv

    # Given an --impressions_file, create an SVMRank formatted output file containing one row per query-doc-features-comments.
    # Looping over impressions, this code issues queries to OpenSearch using the SLTR EXT function to extract LTR feaatures per every query-SKU pair
    # It then optionally normalizes the data (we will not use this in class, but it's there for future use where we don't use XGB, since XGB doesn't need normalization since it's calculating splits)
    # We also apply any click models we've implemented to then assign a grade/relevance score for each and every row.  See click_models.py.
    # Click models can also optionally downsample to create a more balanced training set.
    # Finally, we output two files: 1) training.xgb -- the file to feed to XGB for training
    # 2) training.xgb.csv -- a CSV version of the training data that is easier to work with in Pandas than the XGB file.
    #       This CSV file can be useful for debugging purposes.
    #
    #####

- especially for popular (head) queries: prior user query history is super helpful.
- query logs mimic the popularity of items in the index and helps to mitigate the missing salesRank data.
- Be careful about the "target leakage". This is use of information during training that would not be available during prediction time. This causes the model to be overconfident. 
 - Ensure training & test data are properly split (using future data samples as part of test)
 
