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
    #if test -f "$FILES"; then 
        rm -f "$FILES"
    #fi
    echo "$i deleted"
done

# Shuffle the lines
shuf /workspace/datasets/labeled_query_data_1000.txt > /workspace/datasets/shuffled_query_data.txt
echo "Randomized order of data, shuffled file"

# Make sure all lines are in there
wc -l /workspace/datasets/fasttext/shuffled_query_data.txt

# Split into train and test
head -n 100000 /workspace/datasets/shuffled_query_data.txt > /workspace/datasets/query_class_train.fasttext
tail -n 100000 /workspace/datasets/shuffled_query_data.txt > /workspace/datasets/query_class_test.fasttext
echo "Created training and test files"

# Train with default params
~/fastText-0.9.2/fasttext supervised \
    -input /workspace/datasets/query_class_train.fasttext \
    -output /workspace/models/categories \
    -epoch 20 \
    -wordNgrams 1 \
    -lr 0.5

# Evaluate
#echo "Training with default parameters"
#~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 1
#~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 3
#~/fastText-0.9.2/fasttext test /workspace/models/categories.bin /workspace/datasets/query_class_test.fasttext 5
#echo ""

