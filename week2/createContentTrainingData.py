import argparse
import multiprocessing
import glob
from tqdm import tqdm
import os
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer("english")

def transform_name(product_name: str):
    if args.normalize:
        # Remove all non-alphanumeric characters other than underscore
        product_name = re.sub(r'[^\w_ ]', ' ', product_name)
        # Trim excess space characters so that tokens are separated by a single space.
        product_name = re.sub(r'\s{2,}', ' ', product_name)
        # Convert all letters to lowercase and remove surround whitespace
        product_name = product_name.lower().strip()
        # Stem
        product_name = ' '.join([stemmer.stem(word) for word in product_name.split()])
    return product_name

def filter_products(file_path, min_products):
    # IMPLEMENT:  Track the number of items in each category and only output if above the min
    # Read the whole line is as a single column
    products_df = pd.read_csv(file_path, sep = '\x00', names=['category_product'])
    # Split the first word as the category, all the rest are the product title
    products_df['category'] = products_df['category_product'].str.split().str.get(0)
    products_df['product'] = products_df['category_product'].str.split().str[1:]
    products_df['product'] = products_df['product'].str.join(' ')
    products_df.drop('category_product', axis=1, inplace=True)
    # Filter
    all_labels_df_pruned = products_df[products_df.groupby(['category'])['product'].transform('count') > min_products]
    return all_labels_df_pruned

# Directory for product data
directory = r'/workspace/datasets/product_data/products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--label", default="id", help="id is default and needed for downsteam use, but name is helpful for debugging")
general.add_argument("--normalize", action=argparse.BooleanOptionalAction,  help="Normalize the product names by stripping symbols, applying lowercase and stemming")

# Consuming all of the product data, even excluding music and movies,
# takes a few minutes. We can speed that up by taking a representative
# random sample.
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
names_as_labels = False
if args.label == 'name':
    names_as_labels = True

# all_products_path = '/workspace/datasets/fasttext/labeled_products.txt'

cat_prod_dict = {'category_id': [], 'category_name': [], 'product_name': []}

def _label_filename(filename):

    tree = ET.parse(filename)
    root = tree.getroot()
    labels = []
    for child in root:
        if random.random() > sample_rate:
            continue
        category_path = child.find('categoryPath')
        # Check to make sure category name is valid and not in music or movies
        if (child.find('name') is not None and child.find('name').text is not None and
            category_path is not None and len(category_path) > 0 and
            category_path[len(category_path) - 1][0].text is not None and
            category_path[0][0].text == 'cat00000' and
            category_path[1][0].text != 'abcat0600000'):
              # Choose last element in categoryPath as the leaf categoryId or name
              category_id = category_path[len(category_path) - 1][0].text
              category_name = category_path[len(category_path) - 1][1].text.replace(' ', '_')
              if names_as_labels:
                  cat = category_name
              else:
                  cat = category_id
              # Replace newline chars with spaces so fastText doesn't complain
              name = child.find('name').text.replace('\n', ' ')
              labels.append((cat, transform_name(name)))
            #   cat_prod_dict['category_id'].append(category_id)
            #   cat_prod_dict['category_name'].append(category_name)
            #   cat_prod_dict['product_name'].append(name)
    return labels

if __name__ == '__main__':

    if os.path.isfile(output_file) and min_products > 0:
        all_labels_df_pruned = filter_products(output_file, min_products)
        all_labels_df_pruned['out'] = all_labels_df_pruned['category'] + ' ' + all_labels_df_pruned['product']
        pruned_output_file_path = '/'.join(output_file.split('/')[:-1]) + '/pruned_' + output_file.split('/')[-1]
        all_labels_df_pruned['out'].to_csv(pruned_output_file_path, index=False, header=False)
    else:
        files = glob.glob(f'{directory}/*.xml')

        print("Writing results to %s" % output_file)
        with multiprocessing.Pool() as p:
            all_labels = tqdm(p.imap_unordered(_label_filename, files), total=len(files))

        # all_labels_df = pd.DataFrame.from_dict(cat_prod_dict)
        # all_labels_df_pruned = all_labels_df[all_labels_df.groupby(['category_id'])['product_name'].transform('count') > min_products]
        # if names_as_labels:
        #     all_labels_df_pruned['out'] = '__label__' + all_labels_df_pruned['category_name'] + ' ' + all_labels_df_pruned['product_name']
        # else:
        #     all_labels_df_pruned['out'] = '__label__' + str(all_labels_df_pruned['category_id']) + ' ' + all_labels_df_pruned['product_name']
        # all_labels_df_pruned.to_csv(output_file, index=False, header=False)


            with open(output_file, 'w') as output:
                for label_list in all_labels:
                    for (cat, name) in label_list:
                        output.write(f'__label__{cat} {name}\n')
