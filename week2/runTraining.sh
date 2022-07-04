#!/bin/bash


# LEVEL 1
echo 'Running level 1...'
echo 'Creating Training Data...'
python week2/createContentTrainingData.py --output /workspace/datasets/fasttext/labeled_products.txt
echo 'Filtering Categories...'
python week2/datasetCategoryFilter.py --input /workspace/datasets/fasttext/labeled_products.txt --output /workspace/datasets/fasttext/pruned_labeled_products.txt --minProducts 500
echo 'Shuffling the Data...'
shuf /workspace/datasets/fasttext/pruned_labeled_products.txt > /workspace/datasets/fasttext/shuffled_labeled_products.txt
echo 'Generating Test Data...'
trail -n10000 /workspace/datasets/fasttext/shuffled_labeled_products.txt > /workspace/datasets/fasttext/training_data.txt
echo 'Generating train Data...'
head -n10000 /workspace/datasets/fasttext/shuffled_labeled_products.txt > /workspace/datasets/fasttext/test_data.txt
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/training_data.txt -output /workspace/datasets/fasttext/product_classifier -wordNgrams 2 -lr 1 -epoch 25
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/product_classifier.bin /workspace/datasets/fasttext/test_data.txt 1
