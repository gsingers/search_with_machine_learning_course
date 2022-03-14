import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv

# Useful if you want to perform stemming.
import nltk
nltk.download('punkt')
stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
# Convert the queries to lowercase, strip quotation marks (and perhaps other punctuation), and optionally 
# implement other normalization, like using the nltk stemmer

def normalize(query):
    query = query.lower()
    query = query.replace('"', '').replace('\'', '')
    tokenized_query = nltk.word_tokenize(query)
    tokenized_query = [stemmer.stem(t) for t in tokenized_query]
    query = ' '.join(tokenized_query)
    return query

df['query'] = df['query'].apply(normalize)

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
def num_of_unique_categories():
    return df['category'].nunique()


parent_categories_series = parents_df.set_index('category')['parent']
parent_categories_series[root_category_id] = root_category_id
queries_per_category = df.groupby('category')['query'].nunique()
current_min_queries = queries_per_category.min()
print(f'Before pruning the category tree, there are {num_of_unique_categories()} categories, and the current min_queries is {current_min_queries}.')
while current_min_queries < min_queries:
    small_categories_set = set(queries_per_category[queries_per_category < min_queries].index)
    category_replacements_dict = parent_categories_series[small_categories_set].to_dict()
    df['category'].replace(category_replacements_dict, inplace=True)
    queries_per_category = df.groupby('category')['query'].nunique()
    current_min_queries = queries_per_category.min()
    print(f'num_of_unique_categories() categories for {current_min_queries} unique queries')

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
