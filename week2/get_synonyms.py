import argparse
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import fasttext

model = fasttext.load_model("/workspace/datasets/fasttext/normalized_title_model.bin")
input_file = '/workspace/datasets/fasttext/top_words.txt'
output_file = '/workspace/datasets/fasttext/synonyms.csv'
threshold = 0.75
with open(input_file) as f:
    words = f.readlines()


with open(output_file, "w") as f:
    for w in words:
        synonyms = []
        w = w.strip()
        for n in model.get_nearest_neighbors(w):
            if n[0] >= threshold:
                synonyms.append(n[1])
        if synonyms:
            f.write('{},{}\n'.format(w, ",".join(synonyms)))
