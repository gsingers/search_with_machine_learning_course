import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
import string
import nltk
from nltk.stem.snowball import EnglishStemmer
import pandas as pd

def remove_special_characters(value):
    deletechars = '®™'
    for c in deletechars:
        value = value.replace(c,'')
    return value

def transform_name(product_name):
    # IMPLEMENT - 1 Done
    translation_table = str.maketrans("", "", string.punctuation)
    punctuation_removed_product_name = product_name.translate(translation_table)
    special_characters_removed_product_name = remove_special_characters(punctuation_removed_product_name)
    tokens = special_characters_removed_product_name.split()
    english_stemmer = EnglishStemmer()
    stemmed_tokens = [english_stemmer.stem(token) for token in tokens]
    product_name = " ".join(stemmed_tokens)
    return product_name

# Directory for product data
directory = r'./data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# IMPLEMENT 2 done: Setting min_products removes infrequent categories and makes the classifier's task easier.
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

model_list = []
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
                    # output.write("__label__%s %s\n" % (cat, transform_name(name)))
                    model_list.append([f"__label__{cat}", transform_name(name)])

if min_products > 0:
    print("only include those categories with min products : " + str(min_products))
    df = pd.DataFrame(data=model_list)
    filtered_df = df.groupby(df.columns[0]).filter(lambda category: len(category) >= min_products)
    filtered_df.to_csv(output_file, sep=' ', index=False, header=False)