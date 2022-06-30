DIR="./week2"
DATA_DIR=$DIR"/data"

# create training data
echo "Creating training data"
python week2/createContentTrainingData.py --output $DATA_DIR/labeled_products.txt

# prune
python week2/pruneProducts.py --min_n 500

# shuffle data
echo "Shuffling data"
shuf $DATA_DIR/pruned_labeled_products.txt > $DATA_DIR/shuffled_labeled_products.txt

# train-test split
echo "Creating train and test data"
head -10000 $DATA_DIR/shuffled_labeled_products.txt > $DATA_DIR/pruned_train.txt
tail -10000 $DATA_DIR/shuffled_labeled_products.txt > $DATA_DIR/pruned_test.txt

# train
echo "Training model"
~/fastText-0.9.2/fasttext supervised -input $DATA_DIR/pruned_train.txt -output $DIR/product_classifier -lr 1.0 -epoch 25 -wordNgrams 2

# echo "Evaluating model"
~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/pruned_test.txt 1
~/fastText-0.9.2/fasttext test $DIR/product_classifier.bin $DATA_DIR/pruned_test.txt 10