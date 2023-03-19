import argparse
from pathlib import Path
import os
import fasttext

model_path = r'/workspace/datasets/fasttext/title_model.bin'

# parse command line args
parser = argparse.ArgumentParser(description='Generate synonyms file from fasttext model and top word list.')
general = parser.add_argument_group("general")
general.add_argument("--model", default=model_path,  help="The path to the fasttext skipgram model.")
general.add_argument("--threshold", default=0.75, type=float, help="The cosine similarity threshold used to determine synonyms.")
general.add_argument("--output", default="/workspace/datasets/fasttext/synonyms.csv", help="The file to output to.")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.model:
    model_path = args.model

# load model
title_model = fasttext.load_model(model_path)

# read top words
top_words = []
with open('/workspace/datasets/fasttext/top_words.txt','r') as file:
    top_words = [line.strip() for line in file.readlines()]

# write synonyms file
with open(output_file,'w') as output:
    for word in top_words:
        nn = title_model.get_nearest_neighbors(word,k=20)
        thresholded = [word for (similarity, word) in nn if similarity >= args.threshold]
        if thresholded:
            synonym_rule = ', '.join([word] + thresholded) + '\n'
            output.write(synonym_rule)