import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
import re

# Useful if you want to perform stemming.
import nltk
stemmer = nltk.stem.PorterStemmer()

def transform_query(query: str):
    if args.normalize:
        # Remove all non-alphanumeric characters other than underscore
        query = re.sub(r'[^\w_ ]', ' ', query)
        # Trim excess space characters so that tokens are separated by a single space.
        query = re.sub(r'\s{2,}', ' ', query)
        # Convert all letters to lowercase and remove surround whitespace
        query = query.lower().strip()
    # Stem
    if args.stem:
        query = ' '.join([stemmer.stem(word) for word in query.split()])
    return query

def agg_queries_by_category(query_df: pd.DataFrame, category_map: dict, min_queries: int):
    # This takes a df of queries and their categories and aggregates the queries in each
    # category until there are at least min_queries in each category
    # They are aggregated up to the parent category until the parent has min_queries in it
    count = 0
    while True:
        count += 1
        queries_to_agg = query_df[query_df.groupby(['category'])['cleaned_query'].transform('count') < min_queries]
        if len(queries_to_agg) == 0 or count >= 10:
            break
        df_pruned = query_df[query_df.groupby(['category'])['cleaned_query'].transform('count') >= min_queries]
        # Some categories are not present int the categories file, drop them ie. pcmcat33400050027
        queries_to_agg['category'] = queries_to_agg['category'].apply(lambda cat: category_map.get(cat, np.nan))
        queries_to_agg = queries_to_agg.dropna()
        query_df = pd.concat([df_pruned, queries_to_agg]) 
    return query_df

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")
general.add_argument("--normalize", action=argparse.BooleanOptionalAction,  help="Normalize the product names by stripping symbols, applying lowercase and stemming")
general.add_argument("--stem", action=argparse.BooleanOptionalAction,  help="Apply the Snowball stemmer to the queries")

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
parents_dict = dict(zip(parents, categories))

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
df['cleaned_query'] = df['query'].apply(lambda query: transform_query(query))

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
df_1000 = agg_queries_by_category(df, parents_dict, min_queries)

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['cleaned_query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
