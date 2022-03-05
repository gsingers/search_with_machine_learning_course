import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
from nltk.stem import SnowballStemmer
from collections import Counter
import re

stemmer = SnowballStemmer('english')


def transform_target(child) -> str:
    # print(child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text, [child.find('categoryPath')[i][0].text for i in range(len(child.find('categoryPath')))])
    return child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
    # return child.find('categoryPath')[min(3, len(child.find('categoryPath')) - 1)][0].text


def transform_name(product_name: str) -> str:
    product = re.sub("[^0-9a-zA-Z]+", " ", product_name).lower()
    return " ".join([stemmer.stem(w) for w in product.split()])


# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float,
                     help="The rate at which to sample input (default is 1.0)")
general.add_argument("--min_products", default=0, type=int,
                     help="The minimum number of products per category (default is 0).")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
    os.mkdir(output_dir)

if args.input:
    directory = args.input

min_products = args.min_products
sample_rate = args.sample_rate

categories = []
if min_products > 0:
    print("Counting categories...")
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            print("Processing %s" % filename)
            f = os.path.join(directory, filename)
            tree = ET.parse(f)
            root = tree.getroot()
            for child in root:
                # Check to make sure category name is valid
                if (child.find('name') is not None and child.find('name').text is not None and
                        child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
                        child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None):
                    # Choose last element in categoryPath as the leaf categoryId
                    categories.append(child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text)

counter = Counter(categories)

print("Writing results to %s" % output_file)
with open(output_file, 'w') as output:
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            print("Processing %s" % filename)
            f = os.path.join(directory, filename)
            tree = ET.parse(f)
            root = tree.getroot()
            for child in root:
                if random.random() > sample_rate:
                    continue
                # Check to make sure category name is valid
                if (child.find('name') is not None and child.find('name').text is not None and
                        child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
                        child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None):
                    # Choose last element in categoryPath as the leaf categoryId
                    cat = transform_target(child)
                    # Replace newline chars with spaces so fastText doesn't complain
                    name = child.find('name').text.replace('\n', ' ')
                    if not min_products or counter[cat] > min_products:
                        output.write("__label__%s %s\n" % (cat, transform_name(name)))
