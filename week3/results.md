# Results

## Model: original

###
LR="0.1"
EPOCH="1"
NGRAMS="1"

P@1	0.0192
R@1	0.0192

###
LR="1.0"
EPOCH="25"
NGRAMS="2"

N	9683
P@1	0.658
R@1	0.658

## Model: transformed

```
def transform_name(product_name):
    tokens = word_tokenize(product_name.lower())
    tokens = [stemmer.stem(token) for token in tokens]
    tokens = [token for token in tokens if not token in stop_words]
    tokens = [token for token in tokens if re.search("\w", token) is not None]
    return " ".join(tokens)
```

### no min_products
LR="1.0"
EPOCH="25"
NGRAMS="2"

Number of words:  9540
Number of labels: 1372

P@1	0.648
R@1	0.648

P@5	0.165
R@5	0.824

### min_products 50
LR="1.0"
EPOCH="25"
NGRAMS="2"

Number of words:  9037
Number of labels: 520

P@1	0.762
R@1	0.762

P@5	0.186
R@5	0.928

### min_products 100
LR="1.0"
EPOCH="25"
NGRAMS="2"

Number of words:  8380
Number of labels: 269

P@1	0.831
R@1	0.831

P@5	0.193
R@5	0.965

### min_products 200
LR="1.0"
EPOCH="25"
NGRAMS="2"

Number of words:  7404
Number of labels: 113

P@1	0.906
R@1	0.906

P@5	0.198
R@5	0.99
