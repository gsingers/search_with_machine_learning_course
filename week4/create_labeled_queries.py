import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
from nltk.stem import SnowballStemmer
import re, string

# Useful if you want to perform stemming.
import nltk
#stemmer = nltk.stem.PorterStemmer()

stemmer = SnowballStemmer(language='english')
_re_spec = re.compile(r'([/#\\-\\.:\'\"])')

def spec_add_spaces(t):
    "Add spaces around \" ' . : - / \ and #"
    return _re_spec.sub(r' \1 ', t)

# Causes the resulting RE to match from m to n repetitions of the preceding RE, attempting to match as many repetitions as possible.
_re_space = re.compile(' {2,}')

def rm_useless_spaces(t):
    "Remove multiple spaces"
    return _re_space.sub(' ', t)

def rm_punct(t):
    for p in string.punctuation:
        t = t.replace(p, ' ')
    return t

def transform(query):
    "Transform query by replacing punctuations, removing multiple spaces, stemming, lower casing"
    
    # replace_punct
    query = spec_add_spaces(query)
    
    # remove punct
    query = rm_punct(query)
    
    # replace multiple spaces
    query = rm_useless_spaces(query)

    # fix registered, trademark, copyright symbol
    # remove non-ascii characters from query
    query = query.encode(encoding='ascii', errors='ignore').decode()
    
    query = ' '.join([o for o in query.split(' ') if not o.isnumeric()])
    
    # add stemmer
    query = stemmer.stem(query)
    return query.lower()

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

# IMPLEMENTED: Convert queries to lowercase, and optionally implement other normalization, like stemming.
df['query'] = df['query'].apply(transform)

def parent(cat):
    if cat in parents_df.category.values:
        return parents_df[parents_df.category == cat ].parent.to_list()[0]
    else:
        return root_category_id

# IMPLEMENTED: Roll up categories to ancestors to satisfy the minimum number of queries per category.
cat_count = df.groupby('category').size().to_frame('count')

print(f"# of Categories before pruning : {len(df.category.value_counts())}")

# categories to be pruned
prune_df = cat_count[cat_count['count'] < min_queries];

while len(prune_df) > 0:
    for cat, count in prune_df.iterrows():
        df.replace(to_replace=cat, value=parent(cat), inplace=True)
    cat_count = df.groupby('category').size().to_frame('count')
    prune_df = cat_count[cat_count['count'] < min_queries]
    print(f"Categories to be pruned : {len(prune_df)}")
    
print()
print(f"# of Categories after pruning : {len(df.category.value_counts())}")

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
