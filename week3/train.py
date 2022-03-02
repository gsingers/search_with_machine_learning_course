import fasttext

model_name = "orig"
train_file = "/workspace/datasets/fasttext/%s.fasttext.train" % model_name
test_file = "/workspace/datasets/fasttext/%s.fasttext.test" % model_name

learning_rate = 1.0
epoch = 25
ngrams = 2

print("Training and testing model '%s' with learning_rate %.2f, epoch %d, ngrams %d" % (model_name, learning_rate, epoch, ngrams))

# Train
model = fasttext.train_supervised(input=train_file, lr=learning_rate, epoch=epoch, wordNgrams=ngrams)
print("Model trained")

# Test
print("Testing")
result = model.test(test_file)

def print_results(N, p, r):
    print("N\t" + str(N))
    print("P@{}\t{:.3f}".format(1, p))
    print("R@{}\t{:.3f}".format(1, r))

print_results(*result)

print("Done.")
