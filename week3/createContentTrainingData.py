import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from nltk.stem.snowball import EnglishStemmer

# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

general.add_argument("--max_category_depth", default=0, type=int, help="Categories will be taken at most this distance from the root (default is 0 which means no limit).")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input

min_products = args.min_products
max_cat_depth = args.max_category_depth
sample_rate = args.sample_rate

stemmer = EnglishStemmer()

print("Writing results to %s" % output_file)

def transform_name(product_name):
    product_name = stemmer.stem(product_name)
    return product_name

def parse_child(child):
    name = child.find('name')
    if name is not None and name.text is not None:
        name = name.text.replace('\n', ' ')
    else:
        return

    cat_path = child.find('categoryPath')
    if cat_path is None:
        return

    cat_path_length = len(cat_path)
    if max_cat_depth > 0:
        cat_path_length = min(cat_path_length, max_cat_depth)

    if cat_path_length > 0 and cat_path[cat_path_length - 1][0].text is not None:
        cat = cat_path[cat_path_length - 1][0].text
    else:
        return
    
    return cat, transform_name(name)

def parse_file(filename):
    print("Processing %s" % filename)
    f = os.path.join(directory, filename)
    tree = ET.parse(f)
    root = tree.getroot()
    return [parse_child(child) for child in root if random.random() <= sample_rate]

def parse_all_files():
    rows = sum([parse_file(filename) for filename in os.listdir(directory) if filename.endswith(".xml")], [])
    return pd.DataFrame(rows, columns=['category', 'name']).sample(frac=1).reset_index(drop=True)

def remove_small_categories(df):
    cat_counts = df.groupby('category')['name'].count()
    significant_cats = cat_counts[cat_counts >= min_products].index
    return df[df['category'].isin(significant_cats)]

def write_to_output(df):
    with open(output_file, 'w') as output:
        for category, name in zip(df['category'], df['name']):
            output.write(f"__label__{category} {name}\n")

df = parse_all_files()
df = remove_small_categories(df)
df.to_csv('df.csv', index=False)

write_to_output(df)
