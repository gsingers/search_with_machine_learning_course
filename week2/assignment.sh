# Create training data from BestBuy product data and shuffle
# Label is the category, data is the product name
python week2/createContentTrainingData.py --output /workspace/datasets/fasttext/labeled_products.txt
shuf /workspace/datasets/fasttext/labeled_products.txt > /workspace/datasets/fasttext/shuffled_labeled_products.txt

# Split labeled data into training and test.
head -n 9000 /workspace/datasets/fasttext/shuffled_labeled_products.txt > /workspace/datasets/fasttext/training_data.txt
tail -1000 /workspace/datasets/fasttext/shuffled_labeled_products.txt > /workspace/datasets/fasttext/test_data.txt

# Train model
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/training_data.txt -output bbuy_prod_cat_clf_model
# Test model for P@1 and R@1, P@5 and R@5 and P@10 and R@10
~/fastText-0.9.2/fasttext test bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/test_data.txt
~/fastText-0.9.2/fasttext test bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/test_data.txt 5
~/fastText-0.9.2/fasttext test bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/test_data.txt 10

# Train improved model, set learning rate to 1, epochs to 25 and word ngrams to 2 to learn from bigrams
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/training_data.txt -output bbuy_prod_cat_clf_improved_model -lr 1.0 -epoch 25 -wordNgrams 2
# Test model for P@1 and R@1, P@5 and R@5 and P@10 and R@10
~/fastText-0.9.2/fasttext test bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/test_data.txt
~/fastText-0.9.2/fasttext test bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/test_data.txt 5
~/fastText-0.9.2/fasttext test bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/test_data.txt 10


echo Normalize the dataset

# Preprocess the text and recreate the training and test data
# cat /workspace/datasets/fasttext/shuffled_labeled_products.txt |\
# sed -e "s/\([.\!?,'/()]\)/ \1 /g" |\
# tr "[:upper:]" "[:lower:]" |\
# sed "s/[^[:alnum:]_]/ /g" |\
# tr -s ' ' >\
# /workspace/datasets/fasttext/normalized_labeled_products.txt
python week2/createContentTrainingData.py --normalize --output /workspace/datasets/fasttext/normalized_labeled_products.txt
shuf /workspace/datasets/fasttext/normalized_labeled_products.txt > /workspace/datasets/fasttext/shuffled_normalized_labeled_products.txt
# Split normalized labeled data into training and test.
head -n 9000 /workspace/datasets/fasttext/shuffled_normalized_labeled_products.txt > /workspace/datasets/fasttext/normalized_training_data.txt
tail -1000 /workspace/datasets/fasttext/shuffled_normalized_labeled_products.txt > /workspace/datasets/fasttext/normalized_test_data.txt
# Train model on normalized data
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/normalized_training_data.txt -output normalized_bbuy_prod_cat_clf_model
# Test normalized model for P@1 and R@1, P@5 and R@5 and P@10 and R@10
~/fastText-0.9.2/fasttext test normalized_bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/normalized_test_data.txt
~/fastText-0.9.2/fasttext test normalized_bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/normalized_test_data.txt 5
~/fastText-0.9.2/fasttext test normalized_bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/normalized_test_data.txt 10

# Train improved model, set learning rate to 1, epochs to 25 and word ngrams to 2 to learn from bigrams
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/normalized_training_data.txt -output normalized_bbuy_prod_cat_clf_improved_model -lr 1.0 -epoch 25 -wordNgrams 2
# Test model for P@1 and R@1, P@5 and R@5 and P@10 and R@10
~/fastText-0.9.2/fasttext test normalized_bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/normalized_test_data.txt
~/fastText-0.9.2/fasttext test normalized_bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/normalized_test_data.txt 5
~/fastText-0.9.2/fasttext test normalized_bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/normalized_test_data.txt 10


echo Filter out categories with too few products

python week2/createContentTrainingData.py --normalize --min_products 500 --output /workspace/datasets/fasttext/pruned_labeled_products.txt
shuf /workspace/datasets/fasttext/pruned_labeled_products.txt > /workspace/datasets/fasttext/shuffled_pruned_labeled_products.txt
# Split pruned labeled data into training and test.
head -n 9000 /workspace/datasets/fasttext/shuffled_pruned_labeled_products.txt > /workspace/datasets/fasttext/pruned_training_data.txt
tail -1000 /workspace/datasets/fasttext/shuffled_pruned_labeled_products.txt > /workspace/datasets/fasttext/pruned_test_data.txt
# Train model on pruned data
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/pruned_training_data.txt -output pruned_bbuy_prod_cat_clf_model
# Test pruned model for P@1 and R@1, P@5 and R@5 and P@10 and R@10
~/fastText-0.9.2/fasttext test pruned_bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/pruned_test_data.txt
~/fastText-0.9.2/fasttext test pruned_bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/pruned_test_data.txt 5
~/fastText-0.9.2/fasttext test pruned_bbuy_prod_cat_clf_model.bin /workspace/datasets/fasttext/pruned_test_data.txt 10

# Train improved model, set learning rate to 1, epochs to 25 and word ngrams to 2 to learn from bigrams
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/fasttext/pruned_training_data.txt -output pruned_bbuy_prod_cat_clf_improved_model -lr 1.0 -epoch 25 -wordNgrams 2
# Test model for P@1 and R@1, P@5 and R@5 and P@10 and R@10
~/fastText-0.9.2/fasttext test pruned_bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/pruned_test_data.txt
~/fastText-0.9.2/fasttext test pruned_bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/pruned_test_data.txt 5
~/fastText-0.9.2/fasttext test pruned_bbuy_prod_cat_clf_improved_model.bin /workspace/datasets/fasttext/pruned_test_data.txt 10