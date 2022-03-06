import fasttext
# loss function {ns, hs, softmax, ova} 

model = fasttext.train_unsupervised(input="/workspace/datasets/fasttext/titles.txt", 
  lr=0.2, epoch=40, minCount=50, verbose=2, minn=0, maxn=0, wordNgrams=2, dim=200, ws=3, loss='ns')

model.save_model('titles_model')
