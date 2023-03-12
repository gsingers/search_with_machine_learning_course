import argparse
import fasttext
import csv

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--inputword", default="/workspace/datasets/fasttext/top_words.txt",
                     help="The file containing top words data")
general.add_argument("--inputmodel", default="/workspace/datasets/fasttext/title_model.bin",
                     help="The trained model")
general.add_argument("--output", default="/workspace/datasets/fasttext/synonyms.csv",
                     help="the file to output to")

args = parser.parse_args()
input_word_file = args.inputword
input_model = args.inputmodel
output_file = args.output

if __name__ == '__main__':

    model = fasttext.load_model(input_model)
    threshold = 0.75
    data = []
    with open(input_word_file) as f:
        words = f.readlines()
        for word in words:
            result = model.get_nearest_neighbors(word)
            result_filtered = []
            for synonym in result:
                if synonym[0] >= threshold:
                    result_filtered.append(synonym[1])
            data.append(result_filtered)

    with open(output_file, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)