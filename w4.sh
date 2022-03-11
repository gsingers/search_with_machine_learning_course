# min queries 100
python3 week4/create_labeled_queries.py --min_queries=100 --output .workspace/datasets/labeled_query_data.txt

shuf .workspace/datasets/labeled_query_data.txt \
  > .workspace/datasets/labeled_query_data_shuffled.txt

head -n 50000 .workspace/datasets/labeled_query_data_shuffled.txt \
  > .workspace/datasets/labeled_query_data.train
tail -50000 .workspace/datasets/labeled_query_data_shuffled.txt \
  > .workspace/datasets/labeled_query_data.test

# Train model
fasttext supervised \
  -input .workspace/datasets/labeled_query_data.train \
  -output model_query_cat \
  -lr 0.1 \
  -dim 300 \
  -wordNgrams 2 \
  -epoch 25

# Test model for P@1 and R@1
fasttext test model_query_cat.bin \
  .workspace/datasets/labeled_query_data.test 1

N       49824
P@1     0.518
R@1     0.518

# Test model for P@3 and R@3
fasttext test model_query_cat.bin \
  .workspace/datasets/labeled_query_data.test 3

N       49824
P@3     0.232
R@3     0.697

# Test model for P@5 and R@5
fasttext test model_query_cat.bin \
  .workspace/datasets/labeled_query_data.test 5
N       49824
P@5     0.152
R@5     0.761

# 1000 min queries
python3 week4/create_labeled_queries.py --min_queries=1000 --output .workspace/datasets/labeled_query_data_1000.txt

shuf .workspace/datasets/labeled_query_data_1000.txt \
  > .workspace/datasets/labeled_query_data_shuffled_1000.txt

head -n 50000 .workspace/datasets/labeled_query_data_shuffled_1000.txt \
  > .workspace/datasets/labeled_query_data_1000.train
tail -50000 .workspace/datasets/labeled_query_data_shuffled_1000.txt \
  > .workspace/datasets/labeled_query_data_1000.test

fasttext supervised \
  -input .workspace/datasets/labeled_query_data_1000.train \
  -output model_query_cat_1000 \
  -lr 0.1 \
  -wordNgrams 2 \
  -epoch 25

fasttext test model_query_cat_1000.bin \
  .workspace/datasets/labeled_query_data_1000.test 1

N       49860
P@1     0.516
R@1     0.516

fasttext test model_query_cat_1000.bin \
  .workspace/datasets/labeled_query_data_1000.test 3
N       49860
P@3     0.231
R@3     0.694

fasttext test model_query_cat_1000.bin \
  .workspace/datasets/labeled_query_data_1000.test 5

N       49860
P@5     0.152
R@5     0.758

# all categories

python3 week4/create_labeled_queries.py --output .workspace/datasets/labeled_query_data_all.txt

shuf .workspace/datasets/labeled_query_data_all.txt \
  > .workspace/datasets/labeled_query_data_all_shuffled.txt

head -n 1804998 .workspace/datasets/labeled_query_data_all_shuffled.txt \
  > .workspace/datasets/labeled_query_data_all.train
tail -50000 .workspace/datasets/labeled_query_data_all_shuffled.txt \
  > .workspace/datasets/labeled_query_data_all.test

fasttext supervised \
  -input .workspace/datasets/labeled_query_data_all.train \
  -output model_query_cat_all \
  -minCountLabel 100 \
  -lr 0.5 \
  -dim 100 \
  -wordNgrams 2  \
  -epoch 10

fasttext test model_query_cat_all.bin \
  .workspace/datasets/labeled_query_data_all.test 1

N       47013
P@1     0.615
R@1     0.615
