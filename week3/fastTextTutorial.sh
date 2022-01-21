# Download labeled data
wget https://dl.fbaipublicfiles.com/fasttext/data/cooking.stackexchange.tar.gz
tar xvzf cooking.stackexchange.tar.gz

# Split labeled data into training and test.
head -n -3000 cooking.stackexchange.txt > cooking.train
tail -3000 cooking.stackexchange.txt > cooking.test

# Train model
~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking

# Test model for P@1 and R@1
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test

# Test model for P@5 and R@5
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test 5

# Preprocess the text and recreate the training and test data
cat cooking.stackexchange.txt | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" > cooking.preprocessed.txt
head -n -3000 cooking.preprocessed.txt > cooking.train
tail -n 3000 cooking.preprocessed.txt > cooking.test

# Train and test again
~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test

# Increase number of epochs to 25
~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking -epoch 25
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test

# Increase number of epochs to 100
~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking -epoch 100
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test

# Increase the learning rate to 1.0 and go back to 25 epochs
~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking -lr 1.0 -epoch 25
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test

# Set word ngrams to 2 to learn from bigrams
~/fastText-0.9.2/fasttext supervised -input cooking.train -output model_cooking -lr 1.0 -epoch 25 -wordNgrams 2
~/fastText-0.9.2/fasttext test model_cooking.bin cooking.test








