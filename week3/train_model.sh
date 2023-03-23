bash /workspace/search_with_machine_learning_course/week3/shuffle.sh 9999
head -50000 /workspace/datasets/fasttext/shuf_labeled_queries.txt > /workspace/datasets/fasttext/training_labeled_queries.txt && wc -l /workspace/datasets/fasttext/training_labeled_queries.txt
tail -10000 /workspace/datasets/fasttext/shuf_labeled_queries.txt > /workspace/datasets/fasttext/test_labeled_queries.txt && wc -l /workspace/datasets/fasttext/test_labeled_queries.txt
time ~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/training_labeled_queries.txt -output query_classifier -thread 50 -lr 0.5 -epoch 5 -wordNgrams 3
~/fastText-0.9.2/fasttext test query_classifier.bin /workspace/datasets/fasttext/test_labeled_queries.txt 
~/fastText-0.9.2/fasttext test query_classifier.bin /workspace/datasets/fasttext/test_labeled_queries.txt 2
~/fastText-0.9.2/fasttext test query_classifier.bin /workspace/datasets/fasttext/test_labeled_queries.txt 3
~/fastText-0.9.2/fasttext test query_classifier.bin /workspace/datasets/fasttext/test_labeled_queries.txt 5