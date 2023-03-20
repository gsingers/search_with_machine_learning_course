import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from collections import defaultdict
import csv
import re

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

def sort_categories_by_count(categories):
    return sorted(categories, key=lambda x: category_to_counts.get(x, 0))

def sort_categories_by_topology_and_count(category_to_parent, category_to_counts):
    indegree = defaultdict(int)
    children = defaultdict(list)
    for category, parent in category_to_parent.items():
        indegree[parent] += 1
        if category not in indegree:
            indegree[category] = 0
        children[parent].append(category)

    sorted_categories = []
    layer = [category for category, deg in indegree.items() if deg == 0]
    while layer:
        layer = sort_categories_by_count(layer)
        sorted_categories += layer
        next_layer = []
        for category in layer:
            if category in category_to_parent:
                next_layer.append(category_to_parent[category])
        layer = next_layer
    return sorted_categories

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
category_to_parent = {}
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
        category_to_parent[leaf_id] = cat_path_ids[-2]
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
queries_df = pd.read_csv(queries_file_name)[['category', 'query']]
queries_df = queries_df[queries_df['category'].isin(categories)]    

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
queries_df['query'] = queries_df['query'].apply(
    lambda x: ' '.join([stemmer.stem(word) for word in 
        re.sub(r'\s+', ' ', re.sub(r'[^a-zA-Z0-9]+', ' ', x.lower())).split()])
)

counts = queries_df['category'].value_counts()
category_to_counts = counts.to_dict()

category_to_merged_children = defaultdict(set)  # a category and all the children categories merged into it
category_to_merged_parent = {}  # a category to the parent category that it was merged into

category_to_merged_category = {}
for category in sort_categories_by_topology_and_count(category_to_parent, category_to_counts):
    cur_category = category
    if category not in category_to_counts:
        continue
    cur_count = category_to_counts.get(category, 0)
    parent = category_to_parent.get(category, None)
    if cur_count < min_queries and parent:
        # perform merge
        if parent not in category_to_counts:
            category_to_counts[parent] = cur_count
        else:
            category_to_counts[parent] += cur_count
        category_to_merged_children[parent].add(cur_category)
        category_to_merged_parent[cur_category] = parent
        for merged_category in category_to_merged_children[cur_category]:
            category_to_merged_parent[merged_category] = parent
        cur_category = parent
        cur_count = category_to_counts[parent]


def map_categories(category):
    category = category_to_merged_parent.get(category, category)
    if category == root_category_id or category_to_counts.get(category, 0) < min_queries:
        return None
    else:
        return category


queries_df['category'] = queries_df['category'].apply(map_categories)
queries_df = queries_df[queries_df['category'].notnull().values]

# Create labels in fastText format.
queries_df['label'] = '__label__' + queries_df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
queries_df = queries_df[queries_df['category'].isin(categories)]
queries_df['output'] = queries_df['label'] + ' ' + queries_df['query']
queries_df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
