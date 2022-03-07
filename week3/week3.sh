# Level 1

# Activate python environment
pyenv activate search_with_ml_week3

# gunzip /workspace/search_with_machine_learning_course/data/*/*.xml.gz

python week3/createContentTrainingData.py --output /workspace/datasets/categories/output.fasttext --min_products 5 --shuffle

wc -l /workspace/datasets/categories/output.fasttext 

# Train/test split
head -n -10000 /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/train.fasttext
tail -n -10000 /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/test.fasttext

# Train
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/categories/train.fasttext -output model -lr 1.0 -epoch 2 -thread 32

# Test
~/fastText-0.9.2/fasttext test model.bin /workspace/datasets/categories/test.fasttext
# N       10000
# P@1     0.741
# R@1     0.741

~/fastText-0.9.2/fasttext test model.bin /workspace/datasets/categories/test.fasttext 5
# N       10000
# P@5     0.189
# R@5     0.943

~/fastText-0.9.2/fasttext test model.bin /workspace/datasets/categories/test.fasttext 10
# N       10000
# P@10    0.0966
# R@10    0.967

# Use model interactively:
# ~/fastText-0.9.2/fasttext predict model.bin -

# Questions
# 1. For classifying product names to categories:
# 1.a. What precision (P@1) were you able to achieve?
#   A: P@1 : 0.741
# 1.b. What fastText parameters did you use?
#   A: -lr 1.0 -epoch 2 -thread 32
# 1.c. How did you transform the product names?
#   A: Converted text to lowercase; Removed punctuation, numbers, and any other non alpha tokens; Stemmed tokens
# 1.d. How did you prune infrequent category labels, and how did that affect your precision?
#   A: Removed categories with fewer than 5 observations
# 1.e. How did you prune the category tree, and how did that affect your precision?
#   A: n/a



# Level 2

# Activate python environment
pyenv activate search_with_ml_week3

python week3/extractTitles.py 

# Train model
~/fastText-0.9.2/fasttext skipgram -input /workspace/datasets/fasttext/titles.txt -output /workspace/datasets/fasttext/title_model

~/fastText-0.9.2/fasttext nn /workspace/datasets/fasttext/title_model.bin


# Questions
# 2. For deriving synonyms from content:
# 2.a. What 20 tokens did you use for evaluation?
#   A: 
# 2.b. What fastText parameters did you use?
#   A: 
# 2.c. How did you transform the product names?
#   A: 
# 2.d. What threshold score did you use?
#   A: 
# 2.e. What synonyms did you obtain for these tokens?
#   A: 
