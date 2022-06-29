import argparse
import csv
import fasttext


parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--model_path", default="/workspace/datasets/fasttext/title_model.bin",  help="The path to the model")
general.add_argument("--top_words", default="/workspace/datasets/fasttext/top_words.txt",  help="The path to the text file containing the top words")
general.add_argument("--output", default="/workspace/datasets/fasttext/synonyms.csv", help="the file to output to")

args = parser.parse_args()
model_path = args.model_path
top_words_file = args.top_words
output_file = args.output

# Train model
model = fasttext.load_model(model_path)

# Get nearest neighbours
nns = model.get_nearest_neighbors('iphone')

top_words = []

with open(top_words_file, 'r') as f:
    [top_words.append(word.strip()) for word in f]

with open(output_file, 'w') as output:
    writer = csv.writer(output, delimiter=',', escapechar=' ', quoting=csv.QUOTE_NONE)
    for top_word in top_words:
        row_to_write = [top_word]
        top_word_nns = model.get_nearest_neighbors(top_word) 
        for sim, word in top_word_nns:
            if sim > 0.75:
                row_to_write.append(word)
            else:
                writer.writerow(row_to_write)
                break