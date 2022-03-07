import os
import random
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

import nltk
nltk.download('stopwords')
from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
import string

tokenizer = RegexpTokenizer(r'\w+')
stemmer = SnowballStemmer("english", ignore_stopwords=False)

def transform_training_data(product_name):
    # product_name = stemmer.stem(product_name)
    product_name = product_name.lower()
    product_name = product_name.translate(str.maketrans("", "", string.punctuation))
    product_name = ' '.join(tokenizer.tokenize(product_name))
    return product_name

def main():
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

# Directory for product data
if __name__ == "__main__":
    main()