import argparse
import os
import random
import string
import xml.etree.ElementTree as ET
from pathlib import Path

from nltk.stem import SnowballStemmer
import pandas as pd


stemmer = SnowballStemmer('english')


def transform_name(product_name):
    """Normalize the text of a single product name"""

    pn = product_name

    # lowercase everything
    pn = pn.lower()

    # remove punc characters
    pn = ''.join([c if c not in string.punctuation else ' ' for c in pn])

    # replace all words with stemmed version
    pn = ' '.join([stemmer.stem(w) for w in pn.split()])

    return pn


# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# Setting min_products removes infrequent categories and makes the classifier's task easier.
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

# write all of the unfiltered-by-min-products data out to .csv first
output_file_allcsv = f"{output_file}.all.csv"

print("Writing full results to %s (csv format)" % output_file_allcsv)
with open(output_file_allcsv, 'w') as output:
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
                      output.write("__label__%s,%s\n" % (cat, transform_name(name)))

# Followup and filter out data for categories without min_products
print("Writing filtered-by-min-product results to %s (fasttext input format)" % output_file)
df_x = pd.read_csv(output_file_allcsv, header=None)
df_y = df_x.groupby(0).filter(lambda x: len(x) > min_products)
df_y.to_csv(output_file, sep=' ')
print("done")


