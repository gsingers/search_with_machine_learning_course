# Run the script preparing data for fasttext
python /workspace/search_with_machine_learning_course/week3/createContentTrainingData.py --sample_rate 0.5 --min_products 10

# Shuffle the lines
shuf /workspace/datasets/fasttext/output.fasttext > /workspace/datasets/fasttext/shuffled.fasttext

# Make sure all lines are in there
wc -l /workspace/datasets/fasttext/shuffled.fasttext

# Split into train and test
head -n 10000 /workspace/datasets/fasttext/shuffled.fasttext > /workspace/datasets/fasttext/train.fasttext
tail -n 10000 /workspace/datasets/fasttext/shuffled.fasttext > /workspace/datasets/fasttext/test.fasttext

# Pick out a validation set for autotuning
sed '10001,15001 ! d' /workspace/datasets/fasttext/shuffled.fasttext > /workspace/datasets/fasttext/validate.fasttext

# move to where the data is
cd /workspace/datasets/fasttext

# Train a model
~/fastText-0.9.2/fasttext supervised -input train.fasttext -output products -epoch 50 -wordNgrams 2 -lr 2

# Get the metrics
~/fastText-0.9.2/fasttext test products.bin test.fasttext

# Try looking for hyperparameters automatically
# ~/fastText-0.9.2/fasttext supervised -input train.fasttext -output products_auto -autotune-validation validate.fasttext

# Train with one-vs-all
#~/fastText-0.9.2/fasttext supervised -input train.fasttext -output products -epoch 50 -wordNgrams 2 -lr 0.5
# -loss one-vs-all -minCount 5 -minCountLabel 5