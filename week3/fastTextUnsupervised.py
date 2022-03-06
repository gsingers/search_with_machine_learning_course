import fasttext

model = fasttext.train_unsupervised(input="/workspace/datasets/fasttext/titles.txt", 
  lr=0.2, epoch=40, minCount=50, verbose=True, minn=0, maxn=0, wordNgrams=2, dim=200, ws=3)

model.save_model('titles_model')
