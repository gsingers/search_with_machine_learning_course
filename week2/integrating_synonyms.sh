#!/bin/bash

echo "Selecting 1000 most frequent words"
cat /workspace/datasets/fasttext/normalized_products.txt | tr " " "\n" | grep "...." | sort | uniq -c | sort -nr | head -1000 | grep -oE '[^ ]+$' > /workspace/datasets/fasttext/top_words.txt

echo "Generating synonyms"
python week2/synonym_generator.py

echo "Transfering file to docker container"
docker cp /workspace/datasets/fasttext/synonyms.csv opensearch-node1:/usr/share/opensearch/config/synonyms.csv