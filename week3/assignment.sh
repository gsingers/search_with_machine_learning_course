# grep laptop /workspace/datasets/train.csv | cut -d',' -f3 | python week3/leavesToPaths.py --max_depth 3 | sort | uniq -c | sort -nr | head
# grep laptop /workspace/datasets/train.csv | cut -d',' -f3 | python week3/leavesToPaths.py --max_depth 3 | sort | uniq -c | sort -nr | head

# my naive idea of regex would be (tv)|(laptop)|(music)

# Generate labelled queries+categories with 1k queries/category
# python week3/create_labeled_queries.py --normalize --min_queries 1000 --output /workspace/datasets/fasttext/labeled_queries_1k.txt
shuf /workspace/datasets/fasttext/labeled_queries_1k.txt > /workspace/datasets/fasttext/shuffled_labeled_queries_1k.txt

# Split normalized labeled data into training and test
head -50000 /workspace/datasets/fasttext/shuffled_labeled_queries_1k.txt > /workspace/datasets/fasttext/query_1k_training_data.txt
tail -10000 /workspace/datasets/fasttext/shuffled_labeled_queries_1k.txt > /workspace/datasets/fasttext/query_1k_test_data.txt
# Train model
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/query_1k_test_data.txt -output /workspace/datasets/fasttext/bbuy_query_cat_clf_model_1k
# Test  model for P@1 and R@1, P@3 and R@3 and P@5 and R@5
echo 1k queries/category
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model_1k.bin /workspace/datasets/fasttext/query_1k_test_data.txt
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model_1k.bin /workspace/datasets/fasttext/query_1k_test_data.txt 3
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model_1k.bin /workspace/datasets/fasttext/query_1k_test_data.txt 5

# Generate labelled queries+categories with 10k queries/category
python week3/create_labeled_queries.py --normalize --min_queries 10000 --output /workspace/datasets/fasttext/labeled_queries_10k.txt
shuf /workspace/datasets/fasttext/labeled_queries_10k.txt > /workspace/datasets/fasttext/shuffled_labeled_queries_10k.txt

# Split normalized labeled data into training and test
head -50000 /workspace/datasets/fasttext/shuffled_labeled_queries_10k.txt > /workspace/datasets/fasttext/query_10k_training_data.txt
tail -10000 /workspace/datasets/fasttext/shuffled_labeled_queries_10k.txt > /workspace/datasets/fasttext/query_10k_test_data.txt
# Train model
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/query_10k_test_data.txt -output /workspace/datasets/fasttext/bbuy_query_cat_clf_model_10k
# Test  model for P@1 and R@1, P@3 and R@3 and P@5 and R@5
echo 10k queries/category
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model_10k.bin /workspace/datasets/fasttext/query_10k_test_data.txt
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model_10k.bin /workspace/datasets/fasttext/query_10k_test_data.txt 3
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model_10k.bin /workspace/datasets/fasttext/query_10k_test_data.txt 5