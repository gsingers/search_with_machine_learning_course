import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import pdb

# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/categories/unfiltered_output.fasttext", help="the file to output to")

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

num_products_per_cat_dict = {}


def transform_name(product_name: str):
    """
    Normalize product name for better categorization

    Return: str
    """

    #lowercasing
    product_name = product_name.lower()
    
    # deleting punctuation
    product_name = re.sub(r'(?:[^\w\s]|_)+', ' ', product_name)

    # deleting extra spaces left from deleting punctuation
    product_name = re.sub(' +', ' ', product_name)
    
    # removing stop words
    stop_words = set(stopwords.words('english'))
    product_words = word_tokenize(product_name)
    product_name = [w for w in product_words if w not in stop_words]
    
    # stemming
    stemmer = SnowballStemmer("english")
    product_name = [stemmer.stem(p) for p in product_name]

    # joining BoW back into string
    product_name = ' '.join(product_name)

    return product_name


def write_results_to_output_file_and_return_category_counts_dict() -> dict:
    """
    Iterate through xml input doc & output each item & its corresponding categories.
    Each row in output looks like '__label__abcat0701009 nhl 09 xbox 360'

    Returns: dictionary containing # (int) of products in each category for filtering min_products later on.
    """

    print("Writing results to %s" % output_file)
    with open(output_file, 'w') as output:
        cats = []
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
                        cats.append(cat)
                        # Replace newline chars with spaces so fastText doesn't complain
                        name = child.find('name').text.replace('\n', ' ')
                        output.write("__label__%s %s\n" % (cat, transform_name(name)))
        for i in cats:
            num_products_per_cat_dict[i] = 1 if i not in num_products_per_cat_dict else num_products_per_cat_dict[i]+1
    return num_products_per_cat_dict


def filter_categories(path_to_file_to_filter: str) -> None:
    """
    Read in fastText file with unfiltered categories.
    Filter for only the eligible categories.
    Write new, filtered fastText-formatted output to file 'filtered_output.fasttext'
    """

    # read in original, unfiltered fastText file output by write_results_to_output_file_and_return_category_counts_dict()
    unfiltered_labeled_data_file = open(path_to_file_to_filter, 'r').read().splitlines()

    filtered_labeled_data_lines = []
    for line in unfiltered_labeled_data_file:  # preview: __label__pcmcat196400050016 whirlpool 30 self clean drop electr oven biscuit
        # extract label
        split_line = line.split(' ')
        label = split_line[0].split('__')[-1]
        # only if label is in our dictionary of eligible labels, save it to filtered_labeled_data_lines list
        if label in filtered_dict.keys():
            filtered_labeled_data_lines.append(line)

    # write new, filtered fastText file
    with open('/workspace/datasets/categories/filtered_output.fasttext', 'w') as outfile: 
        for row in filtered_labeled_data_lines:
            outfile.write("%s\n" % row)


if __name__ == '__main__':
     # if you specify a min_products threshold, this will filter out categories below that threshold & write your new output to a file
    if min_products:
        cat_dict = write_results_to_output_file_and_return_category_counts_dict()
        filtered_dict = {k:v for (k,v) in cat_dict.items() if v > min_products}
        unfiltered_labeled_data_file_path = '/workspace/datasets/categories/unfiltered_output.fasttext'
        filter_categories(unfiltered_labeled_data_file_path)
    else:
        write_results_to_output_file_and_return_category_counts_dict()
