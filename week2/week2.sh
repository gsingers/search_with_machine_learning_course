DIR="./week2"
DATA_DIR=$DIR"/data"

# create training data
echo "Creating training data"
python week2/createContentTrainingData.py --output $DATA_DIR/labeled_products.txt

# shuffle data
echo "Shuffling data"
shuf $DATA_DIR/labeled_products.txt > $DATA_DIR/shuffled_labeled_products.txt

# train-test split
echo "Creating train and test data"
head -10000 $DATA_DIR/shuffled_labeled_products.txt > $DATA_DIR/train.txt
tail -10000 $DATA_DIR/shuffled_labeled_products.txt > $DATA_DIR/test.txt

# train model
echo "Training model"
~/fastText-0.9.2/fasttext supervised -input $DATA_DIR/train.txt -output $DIR/product_classifier
chmod ugo+w $DIR/product_classifier.bin
chmod ugo+w $DIR/product_classifier.vec

# Test model for P@1 and R@1
# P@1     0.122
# R@1     0.122
~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/test.txt 1

# Test model for P@5 and R@5
# P@5     0.0419
# R@5     0.209
~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/test.txt 5

# # Test model for P@10 and R@10
# P@10    0.026
# R@10    0.26
~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/test.txt 10

#### test changing the training hyperparams 

# Increase the learning rate to 1.0 and go back to 25 epochs
# P@10    0.0867
# R@10    0.867
# ~/fastText-0.9.2/fasttext supervised -input $DATA_DIR/train.txt -output $DIR/product_classifier -lr 1.0 -epoch 25
# ~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/test.txt 10

# # Set word ngrams to 2 to learn from bigrams
# P@10    0.0864
# R@10    0.864
# ~/fastText-0.9.2/fasttext supervised -input $DATA_DIR/train.txt -output $DIR/product_classifier -lr 1.0 -epoch 25 -wordNgrams 2
# ~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/test.txt 10

### test normalizing the data
# P@1     0.61
# R@1     0.61
# P@10    0.0856
# R@10    0.856
# echo "Normalizing train data"
# cat $DATA_DIR/train.txt |sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > $DATA_DIR/normalized_train.txt
# echo "Normalizing test data"
# cat $DATA_DIR/test.txt |sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" | sed "s/[^[:alnum:]_]/ /g" | tr -s ' ' > $DATA_DIR/normalized_test.txt
# ~/fastText-0.9.2/fasttext supervised -input $DATA_DIR/normalized_train.txt -output $DIR/product_classifier -lr 1.0 -epoch 25 -wordNgrams 2
# ~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/normalized_test.txt 1
# ~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/normalized_test.txt 10

# after implementing transform_name
# create training data
echo "Creating training data"
python week2/createContentTrainingData.py --output $DATA_DIR/labeled_products.txt

# shuffle data
echo "Shuffling data"
shuf $DATA_DIR/labeled_products.txt > $DATA_DIR/shuffled_labeled_products.txt

# train-test split
echo "Creating train and test data"
head -10000 $DATA_DIR/shuffled_labeled_products.txt > $DATA_DIR/train.txt
tail -10000 $DATA_DIR/shuffled_labeled_products.txt > $DATA_DIR/test.txt

# train model
echo "Training model"
~/fastText-0.9.2/fasttext supervised -input $DATA_DIR/normalized_train.txt -output $DIR/product_classifier

# evaluate model
echo "Evaluating model"
~/fastText-0.9.2/fasttext test $DIR/product_classifier $DATA_DIR/test.txt 1
~/fastText-0.9.2/fasttext test $DIR/product_classifier $DATA_DIR/test.txt 10


# after implementing the optional pruning filter
# prune
python week2/pruneProducts.py --min_n=500

# shuffle data
echo "Shuffling data"
shuf $DATA_DIR/pruned_products.txt > $DATA_DIR/shuffled_labeled_products.txt

# train-test split
echo "Creating train and test data"
head -10000 $DATA_DIR/shuffled_labeled_products.txt > $DATA_DIR/pruned_train.txt
tail -10000 $DATA_DIR/shuffled_labeled_products.txt > $DATA_DIR/pruned_test.txt

echo "Training model"
~/fastText-0.9.2/fasttext supervised -input $DATA_DIR/pruned_train.txt -output $DIR/product_classifier -lr 1.0 -epoch 25 -wordNgrams 2