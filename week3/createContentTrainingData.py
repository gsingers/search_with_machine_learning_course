import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import re
import pandas as pd

stemmer = SnowballStemmer("english")
stop_words = set(stopwords.words('english'))


def transform_name(product_name):
    tokens = word_tokenize(product_name.lower())
    tokens = [stemmer.stem(token) for token in tokens]
    tokens = [token for token in tokens if not token in stop_words]
    tokens = [token for token in tokens if re.search("\w", token) is not None]
    return " ".join(tokens)
    # return product_name


# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
# IMPLEMENT:  Track the number of items in each category and only output if above the min
min_products = args.min_products
sample_rate = args.sample_rate

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
                      cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
                      # Replace newline chars with spaces so fastText doesn't complain
                      name = child.find('name').text.replace('\n', ' ')
                      output.write("__label__%s\t%s\n" % (cat, transform_name(name)))

# Only write categories having more than `min_products` products
if min_products > 0:
    print("Only writing categories having more than %d products" % min_products)
    df = pd.read_csv(output_file, names=["category", "product_name"], sep="\t", engine="python")
    categories = df.groupby("category").filter(lambda x: len(x) >= min_products)
    filtered_file = output_file + "_" + str(min_products)
    print("Writing filtered results to %s" % filtered_file)
    categories.to_csv(filtered_file, sep="\t", index=None, header=None)
