import argparse
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import string
import random
from nltk.stem import SnowballStemmer
from collections import defaultdict
# Directory for product data

translator = str.maketrans(string.punctuation, ' '*len(string.punctuation)) #map punctuation to space
stemmer = SnowballStemmer("english")

def transform_name(product_name):
    cleaned = product_name.lower()
    cleaned = cleaned.translate(translator)
    cleaned = stemmer.stem(cleaned)
    return cleaned

directory = r'/workspace/datasets/product_data/products/'
parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=0.05, type=float, help="The rate at which to sample input (default is 0.05)")

# Setting max_input is useful for quick iterations that don't require consuming all of the input or having a representative sample.
general.add_argument("--max_input", default=0, type=int, help="The maximum number of rows to process (0 means no maximum)")

# Setting min_product_names removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_product_names", default=5, type=int, help="The minimum number of products per category.")

# Setting max_product_names makes the category distribution more balanced.
general.add_argument("--max_product_names", default=50, type=int, help="The maximum number of products per category.")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
# IMPLEMENT:  Track the number of items in each category and only output if above the min and below the max
min_product_names = args.min_product_names
max_product_names = args.max_product_names
sample_rate = args.sample_rate
max_input = args.max_input

total_input = 0
cat_freqs = defaultdict(int)
out_dict = defaultdict(list)
print("Writing results to %s" % output_file)
with open(output_file, 'w') as output:
    for filename in os.listdir(directory):
        # Terminate early if max_input is specified and reached.
        if max_input > 0 and total_input == max_input:
            break
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
                      #output.write("__label__%s %s\n" % (cat, transform_name(name)))
                      out_dict[cat].append(transform_name(name))
                      cat_freqs[cat] += 1
                total_input = total_input + 1
                # Terminate early if max_input is specified and reached.
                if total_input == max_input:
                    break
    
    for cat, items in out_dict.items():
        if cat_freqs[cat] >= min_product_names and cat_freqs[cat] <= max_product_names:
            for name in items:
                output.write("__label__%s %s\n" % (cat, name))