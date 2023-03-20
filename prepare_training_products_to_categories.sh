python week2/createContentTrainingData.py --output /workspace/datasets/fasttext/norm_prune_labeled_products.txt --min_products=500
shuf /workspace/datasets/fasttext/norm_prune_labeled_products.txt --random-source=<(seq 99999) > /workspace/datasets/fasttext/shuf_norm_prune_labeled_products.txt
head -10000 /workspace/datasets/fasttext/shuf_norm_prune_labeled_products.txt > /workspace/datasets/fasttext/training_data.txt && wc -l /workspace/datasets/fasttext/training_data.txt 
tail -10000 /workspace/datasets/fasttext/shuf_norm_prune_labeled_products.txt > /workspace/datasets/fasttext/test_data.txt
time ~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/training_data.txt -output product_classifier -lr 1.0 -epoch 25 -wordNgrams 2