# Run the script preparing data for fasttext
python /workspace/search_with_machine_learning_course/week3/extractTitles.py --sample_rate 1

# Train embeddings
cd /workspace/datasets/fasttext/
~/fastText-0.9.2/fasttext skipgram -input titles.txt -output synonyms -minn 2 -maxn 5 -dim 50 -epoch 25 -minCount 5  -lr 0.5 -wordNgrams 2