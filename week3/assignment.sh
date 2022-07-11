# grep laptop /workspace/datasets/train.csv | cut -d',' -f3 | python week3/leavesToPaths.py --max_depth 3 | sort | uniq -c | sort -nr | head
# grep laptop /workspace/datasets/train.csv | cut -d',' -f3 | python week3/leavesToPaths.py --max_depth 3 | sort | uniq -c | sort -nr | head

# my naive idea of regex would be (tv)|(laptop)|(music)

# Generate labelled queries+categories
python week3/create_labeled_queries.py --normalize --stem --min_queries 1000 --output /workspace/datasets/fasttext/labeled_queries.txt
shuf /workspace/datasets/fasttext/labeled_queries.txt > /workspace/datasets/fasttext/shuffled_labeled_queries.txt

# Split normalized labeled data into training and test
head -50000 /workspace/datasets/fasttext/shuffled_labeled_queries.txt > /workspace/datasets/fasttext/query_training_data.txt
tail -10000 /workspace/datasets/fasttext/shuffled_labeled_queries.txt > /workspace/datasets/fasttext/query_test_data.txt
# Train model
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/query_test_data.txt -output /workspace/datasets/fasttext/bbuy_query_cat_clf_model
# Test  model for P@1 and R@1, P@3 and R@3 and P@5 and R@5
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model.bin /workspace/datasets/fasttext/query_test_data.txt
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model.bin /workspace/datasets/fasttext/query_test_data.txt 3
~/fastText-0.9.2/fasttext test /workspace/datasets/fasttext/bbuy_query_cat_clf_model.bin /workspace/datasets/fasttext/query_test_data.txt 5