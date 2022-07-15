# Project week 4

## Hugging face models

```python
from sentence_transformers import SentenceTransformer, util
from itertools import combinations
model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = []
for i in combinations(range(len(sentences)),2):
	print(sentences)
```

config bbuy_products.json BEFORE indexing to use the LM M lib

indexing will take about 40 minutes!
- week 4 removes concurrent file processing
- start query against the index as soon as it starts to receive content to check its working
