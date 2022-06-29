import argparse
import multiprocessing
from collections import defaultdict
import glob
from tqdm import tqdm
import os
import random
import xml.etree.ElementTree as ET
from nltk import stem
from pathlib import Path

stemmer = stem.SnowballStemmer("english")

def transform_name(product_name):
    return stemmer.stem(product_name)

# Directory for product data
DIR = '/Users/tholland/search_with_machine_learning_course/workspace/datasets'
directory = f'{DIR}/product_data/products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default=f"{DIR}/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--label", default="id", help="id is default and needed for downsteam use, but name is helpful for debugging")

# Consuming all of the product data, even excluding music and movies,
# takes a few minutes. We can speed that up by taking a representative
# random sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

general.add_argument("--max_label_depth", default="99", help="how deep in the category path tree to search for the label")

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
names_as_labels = False
if args.label == 'name':
    names_as_labels = True
max_label_depth = int(args.max_label_depth)


def _label_filename(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    labels = []
    for child in root:
        if random.random() > sample_rate:
            continue
        # Check to make sure category name is valid and not in music or movies
        if (child.find('name') is not None and child.find('name').text is not None and
            child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
            child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None and
            child.find('categoryPath')[0][0].text == 'cat00000' and
            child.find('categoryPath')[1][0].text != 'abcat0600000'):
              # Choose last element in categoryPath as the leaf categoryId or name
              cat_path = child.find('categoryPath')
              path_idx = min(len(cat_path) -1, max_label_depth)
              if names_as_labels:
                  cat = cat_path[path_idx][1].text.replace(' ', '_')
              else:
                  cat = cat_path[path_idx][0].text
              # Replace newline chars with spaces so fastText doesn't complain
              name = child.find('name').text.replace('\n', ' ')
              labels.append((cat, transform_name(name)))
    return labels

if __name__ == '__main__':
    files = glob.glob(f'{directory}/*.xml')

    print("Writing results to %s" % output_file)
    with multiprocessing.Pool() as p:
        all_labels = tqdm(p.imap_unordered(_label_filename, files), total=len(files))


        with open(output_file, 'w') as output:
            label_lists = defaultdict(list)
            for label_list in all_labels:
                for (cat, name) in label_list:
                    label_lists[cat].append(name)
            for cat, name_list in label_lists.items():
                if len(name_list) < min_products:
                    continue
                for name in name_list:
                    output.write(f'__label__{cat} {name}\n')



