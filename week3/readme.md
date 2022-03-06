## Setup environment
pyenv activate search_with_ml_week3
alias fasttext=~/fastText-0.9.2/fasttext
pip install nltk
// pip install ipython pandas lxml
// pip install elementpath

## First run
python week3/createContentTrainingData.py

cat /workspace/datasets/fasttext/output.fasttext | sort -R > /workspace/datasets/fasttext/output.fasttext.rand
head -n -10000 /workspace/datasets/fasttext/output.fasttext.rand > /workspace/datasets/fasttext/output.fasttext.train
tail -10000 /workspace/datasets/fasttext/output.fasttext.rand > /workspace/datasets/fasttext/output.fasttext.test

// train
fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs

// test
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       9983
P@1     0.643
R@1     0.643

N       9983
P@5     0.168
R@5     0.842

P@10    0.0883
R@10    0.883

fasttext predict prod_cat.bin -


fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       9983
P@1     0.739
R@1     0.739

N       9983
P@5     0.186
R@5     0.894

N       9983
P@10    0.104
R@10    0.918


---

## Implement transform_name

python week3/createContentTrainingData.py

head /workspace/datasets/fasttext/output.fasttext

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       9984
P@1     0.737
R@1     0.737

N       9984
P@5     0.185
R@5     0.887

N       9984
P@10    0.104
R@10    0.91



## min products


python week3/createContentTrainingData.py --min_products=50

> categories ignored = 1432
> categories written = 520

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.801
R@1     0.801

N       10000
P@5     0.195
R@5     0.939

N       10000
P@10    0.114
R@10    0.958


python week3/createContentTrainingData.py --min_products=200

> categories ignored = 1839
> categories written = 113

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.903
R@1     0.903

N       10000
P@5     0.214
R@5     0.987

N       10000
P@10    0.144
R@10    0.993

## sample rate

python week3/createContentTrainingData.py --min_products=50 --sample_rate=0.3

> categories ignored = 1558
> categories written = 142

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.826
R@1     0.826

N       10000
P@5     0.201
R@5     0.962

N       10000
P@10    0.122
R@10    0.977

## category depth

python week3/createContentTrainingData.py --min_products=200 --cat_depth=2

> categories ignored = 273
> categories written = 149

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.878
R@1     0.878

N       10000
P@5     0.212
R@5     0.974

N       10000
P@10    0.139
R@10    0.983


python week3/createContentTrainingData.py --min_products=100 --cat_depth=2

> categories ignored = 214
> categories written = 208

N       10000
P@1     0.861
R@1     0.861

N       10000
P@5     0.209
R@5     0.966

N       10000
P@10    0.133
R@10    0.977


python week3/createContentTrainingData.py --min_products=50 --cat_depth=2

> categories ignored = 152
> categories written = 270

fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.844
R@1     0.844

N       10000
P@5     0.205
R@5     0.954

N       10000
P@10    0.128
R@10    0.974


## max products - categories balance

python week3/createContentTrainingData.py --min_products=50 --max_products=50 

> categories ignored = 1432
> categories written = 520


fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.709
R@1     0.709

N       10000
P@5     0.174
R@5     0.867

N       10000
P@10    0.0936
R@10    0.908


python week3/createContentTrainingData.py --min_products=50 --max_products=50 --sample_rate=0.3

> categories ignored = 1553
> categories written = 155

$ cat /workspace/datasets/fasttext/output.fasttext | wc -l
> 7595

No point in training.


python week3/createContentTrainingData.py --min_products=50 --max_products=50 --cat_depth=2

> categories ignored = 152
> categories written = 270

$ cat /workspace/datasets/fasttext/output.fasttext | wc -l
> 13230

No point in training.


python week3/createContentTrainingData.py --min_products=200 --max_products=200

> categories ignored = 1839
> categories written = 113

$ cat /workspace/datasets/fasttext/output.fasttext | wc -l
> 22487


fasttext supervised -input /workspace/datasets/fasttext/output.fasttext.train -output prod_cat -loss hs -lr 1 -epoch 20 -wordNgrams 2
fasttext test prod_cat.bin /workspace/datasets/fasttext/output.fasttext.test

N       10000
P@1     0.883
R@1     0.883

N       10000
P@5     0.198
R@5     0.978

N       10000
P@10    0.12
R@10    0.99