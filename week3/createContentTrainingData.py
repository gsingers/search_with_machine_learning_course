import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
from nltk.stem import SnowballStemmer
from nltk import sent_tokenize, word_tokenize

snowball = SnowballStemmer("english") 

def transform_name(product_name):
    # Following http://agailloty.rbind.io/project/nlp_clean-text/
    tokens = word_tokenize(product_name)
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [word.lower() for word in tokens]
    tokens = [snowball.stem(word) for word in tokens]
    transformed_product_name = " ".join(tokens)
    return transformed_product_name

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
# Track the number of items in each category and only output if above the min
registry = {}
categories_in_output = 0
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

                      # Calculate the counts
                      count_by_category = registry.get(cat)
                      if count_by_category is None:
                          registry[cat] = 1
                      else:
                          registry[cat] = count_by_category + 1
                          if count_by_category == min_products:
                              categories_in_output += 1

                      # Don't output records that have less or equal than min_products 
                      if registry[cat] > min_products:
                          output.write("__label__%s %s\n" % (cat, transform_name(name)))

print("Count of categories: ", len(registry.keys()))
print("Count of categories in output: ", categories_in_output)
