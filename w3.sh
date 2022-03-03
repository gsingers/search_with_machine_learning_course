# Create the data files
python week3/createContentTrainingData.py --output /workspace/datasets/categories/output.fasttext --min_products=5

head -n -10000 /workspace/datasets/categories/output.fasttext > week3.train
tail -n -10000 /workspace/datasets/categories/output.fasttext > week3.test

# TODO: normalize the text similarly to the reading material

~/fastText-0.9.2/fasttext supervised -input week3.train -output your_model -lr 1.0 -epoch 1 -wordNgrams 2 -thread 32
# This one is slow, but we'll use it later
# ~/fastText-0.9.2/fasttext supervised -input week3.train -output your_model -lr 1.0 -epoch 25 -wordNgrams 2 -thread 32

~/fastText-0.9.2/fasttext test your_model.bin week3.test
# N       9945
# P@1     0.563
# R@1     0.563

~/fastText-0.9.2/fasttext test your_model.bin week3.test 5
# N       9945
# P@5     0.164
# R@5     0.818

~/fastText-0.9.2/fasttext test your_model.bin week3.test 10
# N       9945
# P@10    0.0868
# R@10    0.868

# With transform name implemented 
# N       9945
# P@10    0.0879
# R@10    0.879

# Interactive testing 
~/fastText-0.9.2/fasttext predict your_model.bin -

# after applying min_products 5 the product count is 106784



