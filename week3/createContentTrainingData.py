import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

# Added imports
import nltk
nltk.download('stopwords')
from nltk.stem.snowball import SnowballStemmer
from collections import Counter
import string

stemmer = SnowballStemmer('english', ignore_stopwords=True)


def transform_name(product_name, lowercase=True, stemming=True, remove_punct=True):
    
    if lowercase == True:
        product_name = product_name.lower()

    if stemming == True:
        product_name = stemmer.stem(product_name)

    if remove_punct == True:
        product_name = product_name.translate(str.maketrans("", "", string.punctuation))

    return product_name

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

# Adding a parameter for how deep into the levels the parser goes
general.add_argument("--level_depth", default=10, type=int, help="The number of levels into the category tree we parse (default is 10).")


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
level_depth = args.level_depth

categories = []

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
                        if len(child.find('categoryPath'))<level_depth:
                            cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
                        else:
                            cat = child.find('categoryPath')[level_depth - 1][0].text
                        categories.append(cat)

                        # Only take categories that are populated by at least n items
                        # It makes sense to do it here, to get better category coverage
                        if cat in [key for key, val in Counter(categories).items() if val>=min_products]:

                            # Replace newline chars with spaces so fastText doesn't complain
                            name = child.find('name').text.replace('\n', ' ')
                            output.write("__label__%s %s\n" % (cat, transform_name(name)))

