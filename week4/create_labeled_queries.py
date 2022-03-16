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


def normalize(queries):
    normalized_queries = []
    for query in queries:
        clean = re.sub(r"[(),:.;@#?!&$/\"-]+\ *", " ", query)
        clean = re.sub(r"[ ]+", " ", clean)
        clean_lc = clean.lower()
        #stemmed = " ".join([stemmer.stem(word) for word in clean_lc.split()])
        normalized_queries.append(clean_lc.replace('\n', ' '))
    return normalized_queries
    

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
print(f"parents_df={parents_df}")
parents_dict = dict(parents_df.values)

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
print(f"queries={df}")
df["query"] = normalize(df["query"])
print("After query normalization:")
print(f"queries={df}")

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
to_rollup = df.groupby("query").filter(lambda x: len(x) < min_queries)
print(f"to_rollup={to_rollup}")

#rolledup_df = to_rollup['category'].transform(lambda x: parents_df.loc[parents_df['category'] == x]['parent'].iloc[0])
to_rollup['category'] = to_rollup['category'].apply(lambda x: parents_dict[x])


#for i, row in to_rollup.iterrows():
#    rolled_up = parents_df.loc[parents_df['category'] == row['category']]['parent'].iloc[0]
#    #print(f"=====\nrolled_up={rolled_up}\n=====\n")
#    dfi = pd.DataFrame({'category': [rolled_up], 'query': [row['query']]})
#    rolledup_df = pd.concat([rolledup_df, dfi], ignore_index=True, axis=0)

print(f"to_rollup={to_rollup}")

df = df[df['query'].isin(to_rollup['query'])]
print(f"After removing to_rollup df={df}")

merged = pd.concat([to_rollup, df], ignore_index=True, axis=0)

print(f"merged={merged}")

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
