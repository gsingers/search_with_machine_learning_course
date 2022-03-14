import os
import random
import string
import unicodedata
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


trans_table = str.maketrans('', '', string.punctuation)
lemmatizer = WordNetLemmatizer()


def remove_punkt(tokens):
    for token in tokens:
        t = token.translate(trans_table)
        if t:
            yield t


def lemmatize(tokens):
    yield from map(lemmatizer.lemmatize, tokens)


token_filters = [
    remove_punkt,
    lemmatize
]

directory = r'/workspace/search_with_machine_learning_course/data/pruned_products'
parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing the products")
general.add_argument("--output", default="/workspace/datasets/fasttext/titles.txt", help="the file to output to")

# Consuming all of the product data takes a while. But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=0.1, type=float, help="The rate at which to sample input (default is 0.1)")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
    os.mkdir(output_dir)

if args.input:
    directory = args.input

sample_rate = args.sample_rate

def transform_training_data(name):
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")
    tokens = word_tokenize(normalized.lower())
    for tf in token_filters:
        tokens = tf(tokens)
    return " ".join(tokens)

# Directory for product data
if __name__ == "__main__":
    nltk.download(["punkt", "stopwords", "wordnet", "omw-1.4"])

    print("Writing results to %s" % output_file)
    with open(output_file, 'w') as output:
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                f = os.path.join(directory, filename)
                tree = ET.parse(f)
                root = tree.getroot()
                for child in root:
                    if random.random() > sample_rate:
                        continue
                    if (child.find('name') is not None and child.find('name').text is not None):
                        name = transform_training_data(child.find('name').text)
                        output.write(name + "\n")
