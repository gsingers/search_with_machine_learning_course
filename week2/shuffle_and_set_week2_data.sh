#!/bin/bash

echo "Normalizing data"
cat /workspace/datasets/fasttext/labeled_products.txt |sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > /workspace/datasets/fasttext/normalized_labeled_products.txt

echo "Shuffling data"
shuf /workspace/datasets/fasttext/normalized_labeled_products.txt --random-source=<(seq 99999) > /workspace/datasets/fasttext/shuffled_labeled_products.txt

echo "Setting train data"
head -10000 /workspace/datasets/fasttext/shuffled_labeled_products.txt > /workspace/datasets/fasttext/training_data.txt

echo "Setting test data"
tail -10000 /workspace/datasets/fasttext/shuffled_labeled_products.txt > /workspace/datasets/fasttext/test_data.txt