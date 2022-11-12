#!/bin/bash

shuf --random-source=<(seq 999999) "/workspace/datasets/fasttext/labeled_queries.txt" > "/workspace/datasets/fasttext/shuffled_labeled_queries.txt"

# Create training & test files
head -10000 "/workspace/datasets/fasttext/shuffled_labeled_queries.txt" > "/workspace/datasets/fasttext/training_labeled_queries.txt"
tail -10000 "/workspace/datasets/fasttext/shuffled_labeled_queries.txt" > "/workspace/datasets/fasttext/test_labeled_queries.txt"

# Create classifier file and test it
queryClassifierFile="/workspace/datasets/fasttext/query_classifier"
~/fastText-0.9.2/fasttext supervised -input "/workspace/datasets/fasttext/training_labeled_queries.txt"  -output "/workspace/datasets/fasttext/query_classifier" -lr 0.25 -epoch 30
~/fastText-0.9.2/fasttext test "/workspace/datasets/fasttext/query_classifier.bin" "/workspace/datasets/fasttext/test_labeled_queries.txt"
