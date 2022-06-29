# Week 2 Content Understanding

Representing information in the index so its discoverable. Our naive starting point was using tokenization.

## Content classification vs Content annontation

Classification maps the content to a topic it is related to (often hierarchical taxonomy) - this is holistic it takes the content as a whole.

Annotation, extracts entities within the content

Rule based classification ie regular expressions - but be careful! Recognize their limits.


## Vectors revisit

Represented mostly as an array, the most important required math is the dot product (multiply the elements in the vector and summing them)


Cosines are just dot products of unit vectors. They are a great way to measure similarity. The angle between a query and document when they are more similar, when they are the same it will have a cosine of 1.


## Content annotation with ML

Training data is labelled examples, it's important the data is representative of the data the model will be given.

- logistic regression
	- takes weight sum and determines it as a value between 0 and 1
	- can be brittle
	- requires normalization
	- often need to pay attention to the features used
- decision trees
	- splitting on values of input to make binary decisions
	- often use ensembles (random forest)
- neural networks

---

Weak supervision is a combination of human generated rules (labeling functions), human labeled representative sample, and few other techniques to train a classifier to label data

---

### Embeddings

Could be words.

Word2Vec


Supervised approaches with embedding ie for content classification and content annotation requires labeled training data

Unsupervised approaches with embedding ie for synonyms and content similarity does not require labeled training data but has no ground truth.

We will use fastText, not the most modern but adequate for our purposes.

CLI (already installed) also accessible from Python.

Annotate to populate facets

Augment the index itself

Use embeddings for dense retrieval (week 4)

Short phrases may require regaining context

Transfer learning (learning on one source and applying to another) might not work well if either are very domain specifying or differently formatted. 

NER (named entity recognition) - don't perform well on short texts (such as queries)

synonyms help with recall but will introduce false positives

https://tech.olx.com/item2vec-neural-item-embeddings-to-enhance-recommendations-1fd948a6f293



## Content understanding

Enrich a piece of content to better represent it's meaning in the index.

*"Simple string processing steps and heuristics like token weighting are only the beginning of content understanding. More sophisticated content understanding uses a combination of holistic (whole-document) and reductionist (focusing on words or phrases) techniques to categorize queries and recognize entities, transforming raw content into a more useful representation. But the variation of content in both size (e.g., short titles, long-form articles) and format (e.g., text,  images) leads to a wide variety of approaches for content understanding."*

## Classification - maps document to topics that can be turned into fields

- flat or hierarchical taxonomy
- better to map documents to leaf nodes but this is not always true for queries
- rule based
	- Hand drawn (ie contains the word `elections` so is classified as `politics`)
	- Output of automation (ie historical human behavior or index statistics)
	- rule based expressions, to go beyond exact token matching to substrings or fuzzy matching
	Open search example

	```sh
	GET /bbuy_products/_search
	{
	"query": {
		"regexp": {
		"name": {
			"flags": "ALL",
			"value": ".*phone.*&~(.*case.*|.*cover.*|.*microphone.*|.*headphone.*)",
			"case_insensitive": true
		}
		}
	}
	}
	```
	Jamie Zawinski said, “Some people, when confronted with a problem, think ‘I know, I'll use regular expressions.’ Now they have two problems.”
- mining rules (heuristic)more holistic approach that considers the document as a whole or at least more of it
	- mining historical searcher behavior (risk is presentation bias - results are only clicked if they are seen)
		- map search queries to categories
		- mine the logs to see what documents users clicked for those queries
		- assign the documents to categories accordingly
- machine-learned classification
	- create training data of labelled examples via explicit human judgments, deriving implicit human judgments from user behavior, or generating heuristic labels. which **must** be representative of the content to which the model will be applied
	- linear model (weighted sum of signals) / decision tree (binary split on whether signal is above threshold) - also mainly using ensemble methods / neural networks
	- test and train data must be separate

## Embedding - transform tokens to vectors

- 1980s: latent semantic indexing (LSI)
	- document-token matrix that assigns a non zero value for each occurrence of a token in a document (ie tf-idf)
	- singular value decomposition allows us to identify the most significant factors of the matrix, which makes it possible to reduce the matrix to a much lower-dimensional approximation (one dimension per concept)
	- this means that if the resulting vectors for two documents in the new vector space are near each other (using the cosine measure discussed earlier), they have similar meanings
- 2000s: latent Dirichlet allocation (LDA)
	- models a document as a distribution of a small number of topics
	- then models each token in the document as corresponding to a distribution of those topics
- word embeddings
	- map tokens, spans of tokens, or entire documents to a vector space
	*“a word is characterized by the company it keeps”*  John Rupert Firth (1950s)

## FastText

### Train model

`~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking`
```
Read 0M words
Number of words:  14543
Number of labels: 735
Progress: 100.0% words/sec/thread:    1757 lr:  0.000000 avg.loss: 10.174898 ETA:   0h 0m 0s
```

### Get Predictions

`~/fastText-0.9.2/fasttext predict model_cooking.bin -`

### Evaluate

`~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test`
```sh

N       3000
P@1     0.143
R@1     0.062
```

### Tune the model

#### Analyzer

```sh
cat cooking.stackexchange.txt | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" > cooking.preprocessed.txt`
head -12404 cooking.preprocessed.txt > cooking.train
tail -3000 cooking.preprocessed.txt > cooking.test
```

#### Increase the Epochs

```sh
~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking -epoch 25
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test
```

#### Learning Rate

Real number between 0 and 1.

```sh
~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking -lr 1.0 -epoch 25
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test
```

#### Hyperparameter optimization 

- automate testing the different tuning parameters

#### ngrams

-  sequence two or more tokens (bigrams are for example a two word phrase)

`-wordNgrams 2`

### FastText in Python

[API DOCs](https://fasttext.cc/docs/en/python-module.html)

```python
import fasttext
help(fasttext.FastText)
```

## Annotation - detects entities that can be turned to fields

- focus on specific word or phrase - entity recognition (faceted attribute-value pairs)
- rule based
	- focuses on tokens or spans of tokens, rather than the document as a whole
	- easier to work with regular expressions than it is for document classification (ie phone number)
- [part-of-speech tagging](https://en.wikipedia.org/wiki/Part-of-speech_tagging) - breaking up nouns, adjectives, verbs
- [named entity recognition (NER)]](https://en.wikipedia.org/wiki/Named-entity_recognition)
- common to first split text into sentences [sentence boundary detection](https://en.wikipedia.org/wiki/Sentence_boundary_disambiguation), this is a challenge of it's own
- it can be hard to evaluate, its often not clear how to measure annotation precision and recall

## Synonyms

- cosine between the two tokens vector is close to 1 then they have similar meaning
- two ways to generate unsupervised models
	- skipgram (can take advantage of contextual information)
	- cbow (continuous bag of words)
- subwords (parts of words) can be useful (especially for rare/ unknown words) but can introduce noise
- nearest neighbors as Synonyms
`~/fastText-0.9.2/fasttext nn wiki.bin`

## Integrating Content Understanding into Search

- Content classification distills a document to what the document is about
- a match between the query and the category name assigned to a piece of content is a strong relevance signal that we can use as a boost or ranking feature
- a category field has much more signal than say perhaps a title field (ie touch pad being a device it's self or part of a device)
- content understanding can help with categorization when say there are new products or occasionally products are showing up with the wrong category 
- it helps make our documents more discoverable
- it also can help us create fields for faceting
- refining on category can help disambiguate the intent  (e.g., “sony” in Televisions vs. Laptops)

## Integrating Content Annotation

- trickier than classification as annotation do no always tell us what a document is about
- specific entity in content may be valuable
- content annotation achieves the most value when it is coupled with query understanding

## Integrating Synonyms

- let the analyzer know about them, the document is then indexed also by these synonyms and not just the tokens
- we want to know whether a result match an original token or because of a synonym in our logs
- in hand tuned model we give a lower boost to synonym matches where as LTR can learn the optimal way to factor them in
- can also be useful for query understanding


