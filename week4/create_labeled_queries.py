import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/fasttext/labeled_query_data.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    directory = args.min_queries

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Map of queries to parents.
parents = {}

# Parse the category XML file to map each category id to its parent category id.
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        parents[leaf_id] = cat_path_ids[-2]

# Read the training data into pandas.
df = pd.read_csv(queries_file_name)[['category', 'query']]

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# IMPLEMENT ME: Trim the queries (some a`qre quoted strings), convert them to lowercase, and optionally
# implement other normalization, like using the nltk stemmer.

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.

# Output labeled query data as a space-separated file.
df[['label', 'query']].to_csv(output_file_name, header=False, sep=' ', index=False)
