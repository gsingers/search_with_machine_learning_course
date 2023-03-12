import argparse
import fasttext
import os
import csv

ROOT_DIR = os.path.dirname(os.path.abspath("__file__"))
MODEL_PATH = os.path.join(ROOT_DIR, 'models/product_synonyms/product_synonyms_mc100_e25.bin')
TOP_WORDS_PATH = os.path.join(ROOT_DIR, 'models/product_synonyms/top_words.txt')
OUTPUT_CSV = os.path.join(ROOT_DIR, 'models/product_synonyms/synonyms.csv')

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--threshold", default=0.75, type=float, help="The minimum NN score to accept word neighbor word as a synonym (range between 0 - 1)")
args = parser.parse_args()

model = fasttext.load_model(path=MODEL_PATH)

with open(TOP_WORDS_PATH) as top_words:
    synonyms=[]
    for line in top_words:
        w = line.rstrip()
        knn = model.get_nearest_neighbors(w)
        fnn = [nn[1] for nn in knn if nn[0] > args.threshold]
        if(len(fnn)):
            synonyms.append(tuple([w]+fnn))

    with open(OUTPUT_CSV,"wt") as syn_file:
        writer = csv.writer(syn_file,delimiter=',')
        writer.writerows(synonyms)