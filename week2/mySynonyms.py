
import pandas as pd
import fasttext

pdf = pd.read_csv("/workspace/datasets/fasttext/top_words.txt",header=None)
pdf.columns = ['words']
print(pdf.head())

model = fasttext.load_model("/workspace/datasets/fasttext/title_model.bin")

myfile = open("/workspace/datasets/fasttext/synonyms.csv",'w')
for word in pdf['words']:
    out = word
    nn_arr = model.get_nearest_neighbors(word)
    for tuple in nn_arr:
        if tuple[0] > 0.7:
            out = out+","+tuple[1]
    myfile.write(out+"\n")
myfile.close()


