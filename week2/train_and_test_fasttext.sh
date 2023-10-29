#!/bin/bash

echo "Starting training of fasttext model"
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/training_data.txt -output model -lr 1.0 -epoch 25 -wordNgrams 2

echo "Testing model"
~/fastText-0.9.2/fasttext test model.bin /workspace/datasets/fasttext/test_data.txt

echo "Predicting data from instructions"
~/fastText-0.9.2/fasttext predict model.bin predict.txt