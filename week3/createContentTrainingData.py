import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import nltk
nltk.download('stopwords')

from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer

import string

tokenizer = RegexpTokenizer(r'\w+')
stemmer = SnowballStemmer("english", ignore_stopwords=False)

def transform_name(product_name):
    product_name = stemmer.stem(product_name)
    product_name = product_name.translate(str.maketrans("", "", string.punctuation))
    product_name = ' '.join(tokenizer.tokenize(product_name))
    return product_name

# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=50, type=int, help="The minimum number of products per category (default is 50).")

# Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--cat_depth", default=1, type=int, help=" How granular should be categories (default is 1 - which means depth = leaf-1).")

# Setting max_products force class balance
general.add_argument("--max_products", default=0, type=int, help="The maximum number of products per category (default is 0, off).")


args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
# Track the number of items in each category and only output if above the min
min_products = args.min_products
max_products = args.max_products

sample_rate = args.sample_rate
cat_depth = args.cat_depth

categries = {}
bufferedWrited = {}

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

                catIdx = len(child.find('categoryPath'))
                catIdx = catIdx - (cat_depth)
                catIdx = max(0, catIdx)

                # Check to make sure category name is valid
                if (child.find('name') is not None and child.find('name').text is not None and
                    child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
                    child.find('categoryPath')[catIdx][0].text is not None):
                      # Choose last element in categoryPath as the leaf categoryId
                      cat = child.find('categoryPath')[catIdx][0].text
                      # Replace newline chars with spaces so fastText doesn't complain
                      name = child.find('name').text.replace('\n', ' ')
                      
                      if cat not in categries:
                          categries[cat] = 0
                          bufferedWrited[cat] = []
                    
                      categries[cat] = categries[cat] + 1

                      if categries[cat] < min_products:
                          print("buffer cat {} \t len={} \n".format(cat, categries[cat]))
                          bufferedWrited[cat].append((cat, transform_name(name)))
                          continue

                      if len(bufferedWrited[cat]) > 0:
                          print("flush  cat {} \t len={} \n".format(cat, categries[cat]))
                          for tuple in bufferedWrited[cat]:
                             output.write("__label__%s %s\n" % tuple)
                          bufferedWrited[cat] = []
                          continue

                      if max_products > 0 and categries[cat] > max_products:
                          print("max  cat {} \t len={} \n".format(cat, categries[cat]))
                          continue

                      
                      print("write  cat {} \t len={} \n".format(cat, categries[cat]))
                      output.write("__label__%s %s\n" % (cat, transform_name(name)))

    bufferedCategories = 0
    writtenCategories = 0
    for cat in bufferedWrited.keys():
        if len(bufferedWrited[cat]) > 0:
            bufferedCategories += 1
        else:
            writtenCategories += 1

    print("categories ignored = {}".format(bufferedCategories))
    print("categories written = {}".format(writtenCategories))
        

