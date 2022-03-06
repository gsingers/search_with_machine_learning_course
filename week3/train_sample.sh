#~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/cats.train -output /workspace/datasets/fasttext/model_sample -wordNgrams 2
# punct -> space
# punct -> space && lowercase
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/cats_punct_to_space_lc.train -output /workspace/datasets/fasttext/model_sample_punct_to_space_lc -loss hs -wordNgrams 2 -epoch 25 -lr 0.8 --min_products 50