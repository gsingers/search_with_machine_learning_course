# Week 4

## Class notes

- Tuesday Fire side with Dave Lewis (litigation (eDiscovery), corporate investigations, regulatory and information governance.)
- Wednesday project kick off
- Friday community share out
- submit 3/4 projects to get a certificate.

### Limitations of inverted index

- struggles with understanding sentiment and the similarity of meaning between sentences based on it's words (tokens)

### Vector search

- computer relevancy from query to document

In long queries, we might not know which words can be removed, or how to expand a query. However inverted index can sometimes do very well, ie looking for specific information. Vector search is good at general topic but not for fine grain control and additionally is slower than inverted index.

#### Representing documents as vectors

- get a single string that is normalized out into language model to create vector
- check out hugging face course on tokenization
- unlikely you train a model from scratch, more likely to fine tune the final layers of a pre built one

#### Representing Queries as vectors

- can use same model if the queries look similar (same normalization, same vocabulary, same style) as documents
- use two tower model
- aggregate on the vectors, to move query vector to same vector space as document. Good for head and torso queries, hard for tail queries

#### Retrieval: nearest neighbor search

- approximate nearest neighbor search, hierarchal small worlds (HNSW)
- 

**Search is not only indexing, ranking, query understanding etc**

### Project 4

- KNN plug in for OpenSearch
- Hugging face sentence transformers
- 

Query independent factors often require some normalization (ie price), if some overlap think about combining them to create features.

Query dependent factors, look at individual field and try to find what 

### References

- [AI for Query Understanding](https://dtunkelang.medium.com/ai-for-query-understanding-d8c073095fff)
- [Hugging Face course](https://huggingface.co/course/chapter0/1?fw=pt)
- [Semantic Product search](https://arxiv.org/pdf/1907.00937.pdf)
- [Extreme multi-label learning for semantic matching in product search](https://arxiv.org/abs/2106.12657)
- [Evaluating search](https://dtunkelang.medium.com/evaluating-good-search-part-i-measure-it-5507b2dbf4f6)
- [Introduction to Information Retrieval (2008)](https://nlp.stanford.edu/IR-book/information-retrieval-book.html)
- [Modern Information Retrieval](https://www.amazon.com/Modern-Information-Retrieval-Concepts-Technology-dp-0321416910/dp/0321416910/ref=dp_ob_title_bk)


## Vector Search

*"represents both the content and queries as vectors, typically through the use of word embeddings, and then retrieves and ranks results based on a distance or similarity function that describes the relationship between those vectors."*

- directly compute the relevance of a document to a query using representation of both that holistically represent their meaning
- traditional inverted index is challenged by words with multiple meanings (polysemy) which can result in a loss of precision, vector representation can, at least in theory, avoid this.
- synonyms and word variants can be addressed through techniques like stemming and dictionary-based query expansion, those don't scale well for tail queries. Vector representations are not subject to the "Vocabulary problem", multiple words that express the same meaning.
- inverted index applications can struggle with long queries, resorting to query relation to ensure recall but often at the expense of precision, in contrast vector search represents the query holistically so this precision-recall tradeoff doesn't happen

**However**

- vectors from word embeddings tend to be a lot less explainable than tokens, making them a bit of a black box
- a single embedding may not capture everything about a document or query and tend to be task dependant
- embedding vectors have large dimensions!
- vector search relies on an index designed for nearest-neighbor search, this is slower and less efficient
- vector search returns relevancy but not ranking, its hard to combine query dependent factors
- If we want to combine the output of a similarity search with facets, filters, or token-based retrieval, we're likely to incur a significant cost because of the different sort orders.

## Populating a Vector Search Index

- representing the document as a single string
	- how to handle
		- multiple fields
		- non-textual fields
		- long documents (to summarize)
		- normalization and tokenization
	- approach
		- text normalization removing special characters and punctuation
		- select high-signal fields such as title, you may also want to combine them
		- convert non-text fields to text, ie use a category name over it's id

### To build or borrow a language Model

- building from scratch means the model focuses on the vocabulary of our documents
- however its expensive and requires huge amounts of data
- off the shelf models on the other hand are pre-trained but they might not know about the unique vocabulary or style of our documents
- with fine-tuning we can start with a pre-trained model but then adapt it to our data set. [Article about fine-tuning](https://huggingface.co/docs/transformers/training)

### Indexing documents

After establishing a model to transform documents to vectors we need to index them for retrieval and ranking.

- naive indexing, query vector similarity to our document vector (slow due to computation to vectorized the query and dot product on a pair of large vectors)
- another approach could be to organize vectors into clusters (balancing coherence and distinctiveness)
- nearest neighbor indexing relies on Hierarchical Navigable Small Worlds (HNSW) which use the idea of greedy traversal to achieve an efficient data structure for approximate nn search. This structure keeps the most similar vectors very near to one another but ensures even far away vectors have relatively short paths connecting them. This is combined with a data structure called a skip list, a multi layered linked list that enables fast lookup and insertion.

### Retrieval and ranking

- to transform the query to a vector we can use the same model, if our query is similar in style and vocabulary to our documents
- when the query and document differ too greatly it's better to train two neural network models, in what is know as a two-tower model. [Google course on two tower models](https://cloud.google.com/vertex-ai/docs/matching-engine/train-embeddings-two-tower)
- another approach could be to use aggregations such as mapping a query to the documents that people click on, this generally has to happen offline so only works well for a known set of queries
- **measuring vector similarity** we can calculate the distance with a function such as [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) or [Cosine similarity]()https://en.wikipedia.org/wiki/Cosine_similarity note that cosine simlarity does not respect the triangle inequality and thus is not a true metric.
- **relevance versus ranking** ranking takes into account additional attribute such as popularity, desirability, quality or other subjective factors whereas relevance measure to what extent a result is close to the query.
- similarity score is a query-dependant factor but it can be brittle and susceptible to error and bias
- consider to use a machine learning approach that plays well with nonlinearity such as the tree-based XGboost
- product quantization: a technique compressing vectors to reduce their memory footprint and computation required at query time is common

### Combining Vector search with traditional search

To get the best of both world we can combine the two.

- filtering the results of a vector search using an entry in the inverted index, but what happens if there is no overlap, should it return a small or empty dataset or dig deeper into the nearest neighbor list to find a result that overlaps with the filter?
- allow users to sort results (ie by price), it's important retrieval has a reasonable level of precision. since there's no absolute similarity threshold (its non linear) the choice of threshold is a precision-recall tradeoff, if we retrieve more results we risk sorting putting irrelevant results at the top

### Cost of operations

- operations such as insertion, union and negation are more expensive with nearest neighbor search when we combine them with filters or token based retrieval, we have to first sort the results by document ID and that cost is proportional to the number of results

## Putting it into Practice using OpenSearch

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers import util
from itertools import combinations

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
sentences = ['I am a cat', 'I am a kitten', 'I am not a cat', 'I am a dog', 'I am a hot dog']
embeddings = model.encode(sentences)
for i in combinations(range(len(sentences)), 2):
   print(sentences[i[0]] + ',' + sentences[i[1]] + ': ' + \ 
   str(util.cos_sim(embeddings[i[0]],embeddings[i[1]])))
```

```
I am a cat,I am a kitten: tensor([[0.9004]])
I am a cat,I am not a cat: tensor([[0.6957]])
I am a cat,I am a dog: tensor([[0.6201]])
I am a cat,I am a hot dog: tensor([[0.3863]])
I am a kitten,I am not a cat: tensor([[0.6399]])
I am a kitten,I am a dog: tensor([[0.5425]])
I am a kitten,I am a hot dog: tensor([[0.3441]])
I am not a cat,I am a dog: tensor([[0.4558]])
I am not a cat,I am a hot dog: tensor([[0.2316]])
I am a dog,I am a hot dog: tensor([[0.6669]])
```
