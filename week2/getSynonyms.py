import pandas as pd 
import fasttext 


model = fasttext.load_model("/workspace/datasets/fasttext/title_model.bin")
top_words = pd.read_table("/workspace/datasets/fasttext/top_words.txt", header=None)

_THRESHOLD = 0.75

words_w_nn = []
for _, row in top_words.iterrows():
    nn = model.get_nearest_neighbors(row[0])
    nn_filtered = [n[1] for n in nn if n[0] > _THRESHOLD]
    word_w_nn = [row[0]] + nn_filtered
    words_w_nn.append(word_w_nn)

df_words_w_nn = pd.DataFrame(words_w_nn)
df_words_w_nn.to_csv("/workspace/datasets/fasttext/synonyms.csv", header=False, index=False)