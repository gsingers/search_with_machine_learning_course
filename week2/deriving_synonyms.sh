#!/bin/bash

echo "Outputing categories names"
python week2/createContentTrainingData.py --output /workspace/datasets/fasttext/products.txt --label name

echo "Normalizing text"
cat /workspace/datasets/fasttext/products.txt |  cut -c 10- | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]]/ /g" | tr -s ' ' > /workspace/datasets/fasttext/normalized_products.txt

echo "Creating model"
~/fastText-0.9.2/fasttext skipgram -input /workspace/datasets/fasttext/normalized_products.txt -output /workspace/datasets/fasttext/title_model_100 -minCount 100 -epoch 25

echo "Getting nearest neighbors"
~/fastText-0.9.2/fasttext nn /workspace/datasets/fasttext/title_model.bin