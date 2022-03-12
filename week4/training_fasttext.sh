# List the files created each run
declare -a FILES=(
    "/workspace/datasets/shuffled_query_data.txt" 
    "/workspace/datasets/query_class_train.fasttext"
    "/workspace/datasets/query_class_test.fasttext" 
    "/workspace/models/categories.bin"
    "/workspace/models/categories.vec")

# If they're there, remove them
for i in "${FILES[@]}"
do
    if test -f "$FILES"; then 
        rm -f "$FILES"
    fi
done

# Shuffle the lines
shuf /workspace/datasets/labeled_query_data_1000.txt > /workspace/datasets/shuffled_query_data.txt

# Make sure all lines are in there
wc -l /workspace/datasets/fasttext/shuffled_query_data.txt

# Split into train and test
head -n 50000 /workspace/datasets/shuffled_query_data.txt > /workspace/datasets/query_class_train.fasttext
tail -n 50000 /workspace/datasets/shuffled_query_data.txt > /workspace/datasets/query_class_test.fasttext

# Train with default params
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/query_class_train.fasttext -output /workspace/models/categories

# Evaluate
echo "Training with default parameters"
~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 1
~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 3
~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 5
rm -f /workspace/models/categories.bin
rm -f /workspace/models/categories.vec

# Varying learning rate
declare -a LR=("0.1" "0.3" "0.5" "0.7")
for i in "${LR[@]}"
do
    echo "Learning rate set to ${i}"
    ~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/query_class_train.fasttext -output /workspace/models/categories -lr ${i}
    # Evaluate
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 1
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 3
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 5
    rm -f /workspace/models/categories.bin
    rm -f /workspace/models/categories.vec
    echo ""
done

# Varying epochs
declare -a EPOCH=("5" "10" "15", "20")
for i in "${EPOCH[@]}"
do
    echo "Epochs set to ${i}"
    ~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/query_class_train.fasttext -output /workspace/models/categories -epoch ${i}
    # Evaluate
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 1
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 3
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 5
    rm -f /workspace/models/categories.bin
    rm -f /workspace/models/categories.vec
    echo ""
done

# Varying ngrams
declare -a NGRAM=("1" "2" "3")
for i in "${NGRAM[@]}"
do
    echo "Word ngram set to ${i}"
    ~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/query_class_train.fasttext -output /workspace/models/categories -wordNgrams ${i}
    # Evaluate
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 1
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 3
    ~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 5
    rm -f /workspace/models/categories.bin
    rm -f /workspace/models/categories.vec
    echo ""
done