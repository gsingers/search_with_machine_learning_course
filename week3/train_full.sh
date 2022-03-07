# generic command
#~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/full_cats_punct_to_space_lc.train -output /workspace/datasets/fasttext/full_model_sample_punct_to_space_lc -loss hs -epoch 100 -lr 0.1 -wordNgrams 2
#~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/output_punct_to_space.fasttext.orig.shuffled.train -output /workspace/datasets/fasttext/full_model_sample_punct_to_space_lc -loss hs
# with min_products=50
#~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/output_punct_to_space_lc.fasttext_50.train -output /workspace/datasets/fasttext/full_model_fifty1 -loss hs -epoch 100
# with min_products=100
#~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/output_punct_to_space_lc.fasttext_100.train -output /workspace/datasets/fasttext/full_model_100 -loss hs -epoch 100
# with min_products=200
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/output_punct_to_space_lc.fasttext_200.train -output /workspace/datasets/fasttext/full_model_200 -loss hs -epoch 100
