import nltk

nltk.download('averaged_perceptron_tagger')

str = "Cats eat raw fish."
tokens = nltk.word_tokenize(str)
nltk.pos_tag(tokens)
