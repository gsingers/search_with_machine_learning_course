echo "min_products 50"
python week3/createContentTrainingData.py --output /workspace/datasets/categories/output.fasttext --min_products 50
shuf /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.fasttext.shuffled
mv /workspace/datasets/categories/output.fasttext.shuffled /workspace/datasets/categories/output.fasttext
head -n -3000 /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.train
tail -3000 /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.test
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/categories/output.train -output prune_products_model -lr 1.0 -epoch 25 -wordNgrams 2
~/fastText-0.9.2/fasttext test prune_products_model.bin /workspace/datasets/categories/output.train


echo "min_products 100"
python week3/createContentTrainingData.py --output /workspace/datasets/categories/output.fasttext --min_products 100
shuf /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.fasttext.shuffled
mv /workspace/datasets/categories/output.fasttext.shuffled /workspace/datasets/categories/output.fasttext
head -n -3000 /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.train
tail -3000 /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.test
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/categories/output.train -output prune_products_model -lr 1.0 -epoch 25 -wordNgrams 2
~/fastText-0.9.2/fasttext test prune_products_model.bin /workspace/datasets/categories/output.train


echo "min_products 200"
python week3/createContentTrainingData.py --output /workspace/datasets/categories/output.fasttext --min_products 200
shuf /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.fasttext.shuffled
mv /workspace/datasets/categories/output.fasttext.shuffled /workspace/datasets/categories/output.fasttext
head -n -3000 /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.train
tail -3000 /workspace/datasets/categories/output.fasttext > /workspace/datasets/categories/output.test
~/fastText-0.9.2/fasttext supervised -input /workspace/datasets/categories/output.train -output prune_products_model -lr 1.0 -epoch 25 -wordNgrams 2
~/fastText-0.9.2/fasttext test prune_products_model.bin /workspace/datasets/categories/output.train