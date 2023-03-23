import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
import re
from tqdm import tqdm
import time
# Useful if you want to perform stemming.
import nltk
stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/fasttext/labeled_queries.txt'

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
queries_df = pd.read_csv(queries_file_name)[['category', 'query']]
def normalization(query):
    return ' '.join([stemmer.stem(word) for word in re.sub('[^a-z0-9\w]', ' ', query.lower().strip()).split(' ')])

queries_df = queries_df[queries_df['category'].isin(categories)]
print("Start normalization:")

tqdm.pandas()
queries_df['query'] = queries_df['query'].progress_apply(normalization)

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.

# Create labels in fastText format.
cat_cnts = queries_df.groupby(['category']).size().sort_values(ascending=False) .reset_index(name='cat_count') 
cat_less_q = cat_cnts[cat_cnts['cat_count'] < min_queries]['category'].unique()
initial_len = len(cat_less_q)
print("Starting the prune day")
pbar = tqdm(total=initial_len)
while cat_less_q.shape[0] > 0:
    current_cat = cat_less_q[0]
    parent_df = parents_df[parents_df['category']==current_cat]['parent']
    if parents_df[parents_df['category']==current_cat]['parent'].shape[0] > 0:
        parent_cat = parent_df.values[0]
        parent_df_cnt = cat_cnts[cat_cnts['category']==parent_cat]['cat_count']
        if parent_df_cnt.shape[0] > 0:
            parent_cat_count = parent_df_cnt.values[0]
        else:
            parent_cat_count = 0
        current_cat_cnt = cat_cnts[cat_cnts['category']==current_cat]['cat_count'].values[0]
        
        queries_df.loc[(queries_df['category'] == current_cat),'category'] = parent_cat
        cat_cnts.loc[(cat_cnts['category'] == current_cat),'category'] = parent_cat
        cat_cnts.loc[(cat_cnts['category'] == parent_cat),'cat_count'] = current_cat_cnt + parent_cat_count
        
        cat_less_q = cat_cnts[cat_cnts['cat_count'] < min_queries]['category'].unique()
        pbar.update(initial_len - len(cat_less_q) - pbar.n)
    else:
        cat_less_q = cat_less_q[cat_less_q != current_cat]
        pbar.update(initial_len - len(cat_less_q)- pbar.n)
        
queries_df['cat_count'] = queries_df.groupby('category')['category'].transform('count')
print(queries_df)
queries_df['label'] = '__label__' + queries_df['category']
# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
queries_df = queries_df[queries_df['category'].isin(categories)]
queries_df['output'] = queries_df['label'] + ' ' + queries_df['query']
queries_df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
