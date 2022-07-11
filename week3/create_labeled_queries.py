import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
import re
from sklearn.utils import shuffle 

# Useful if you want to perform stemming.
from nltk.stem.snowball import EnglishStemmer
stemmer = EnglishStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=10,  help="The minimum number of queries per category label (default is 10)")
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

# parents_df.to_csv('/workspace/datasets/parent_cats.csv', index=False, encoding="utf-8")
# parents_df = pd.read_csv('/workspace/datasets/parent_cats.csv')

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)].sort_values('category')
df = df.merge(parents_df, on='category')

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
pattern_keep = re.compile(r"[^a-zA-Z0-9 ]")
df['query'] = df['query'].apply(lambda x: stemmer.stem(re.sub(' +',' ',re.sub(pattern_keep, '', x.lower()))))

# df.to_csv('/workspace/datasets/my_processed_queries.csv', index=False, encoding="utf-8")
# df = pd.read_csv('/workspace/datasets/my_processed_queries.csv')

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
while True:
    t = df.groupby('category')['query'].count().reset_index(name='query_cnt').sort_values('query_cnt')
    # print(t.head())
    df = df.merge(t,on='category')
    df['category'] = np.where(df['query_cnt'] < min_queries, df['parent'], df['category'])
    df.drop(columns=['query_cnt','parent'], inplace=True)
    df = df.merge(parents_df, on='category')
    t = df.groupby('category')['query'].count().reset_index(name='query_cnt').sort_values('query_cnt')
    if t['query_cnt'].min() >= min_queries:
        break

# print(df.groupby('category')['query'].count().reset_index(name='query_cnt'))
df.drop(columns=['parent'], inplace=True)
print(df.head())

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df = shuffle(df)
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
