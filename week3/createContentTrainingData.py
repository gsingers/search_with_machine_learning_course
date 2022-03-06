import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import re
from nltk.stem import SnowballStemmer

import pandas as pd

stemmer = SnowballStemmer(language='english')
_re_spec = re.compile(r'([/#\\-\\.:])')

def spec_add_spaces(t):
    "Add spaces around . : - / \ and #"
    return _re_spec.sub(r' \1 ', t)

# Causes the resulting RE to match from m to n repetitions of the preceding RE, attempting to match as many repetitions as possible.
_re_space = re.compile(' {2,}')

def rm_useless_spaces(t):
    "Remove multiple spaces"
    return _re_space.sub(' ', t)

def transform_name(product_name):
    "Transform product name by replacing punctuations, removing multiple spaces, stemming, lower casing"
    name = product_name

    # replace_punct
    name = spec_add_spaces(name)
    # replace multiple spaces
    name = rm_useless_spaces(name)

    # add stemmer
    name = stemmer.stem(name)
    return name.lower()

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
min_products = args.min_products
sample_rate = args.sample_rate

items = []

## Reads from the xml and adds cat, name as `tuple` to the items `list`
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

                items.append((cat, transform_name(name))
                #output.write("__label__%s %s\n" % (cat, transform_name(name)))

# IMPLEMENT:  Track the number of items in each category and only output if above the min

# Load the items into a dataframe.
df = pd.DataFrame(items, columns=['cat', 'name'])
                             
def filter_by_min_products(df, minimum=50):
    "Filter the dataframe to categories of threshold set with minimum"
    tmp = pd.DataFrame(df.cat.value_counts())
    min_filter = tmp[tmp['cat'] > minimum]
    return df[df.cat.isin(min_filter.index)]
                             
def write_output(df, output_file = r'/workspace/datasets/fasttext/output.fasttext', minimum=50):
    filtered_df = filter_by_min_products(df, minimum)
    with open(output_file, 'w') as output:
        for _, item in filtered_df.iterrows():
            output.write("__label__%s %s\n" % (item['cat'], item['name']))
                             
print("Writing results to %s" % output_file)
write_output(df, output_file, minimum=min_products)