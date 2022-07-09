import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv

# Useful if you want to perform stemming.
import nltk
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

def stem(query: str):
    query_split = query.split(' ')
    stemmed = [stemmer.stem(w) for w in query_split]
    sentence = " ".join(stemmed)
    return sentence

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
#df = pd.read_csv(queries_file_name)[['category', 'query']]
#df = df[df['category'].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
#df['query'] = df['query'].apply(lambda x: x.lower())
#df['query'] = df['query'].apply(lambda x: stem(x))
#print(df.head(20))
#df.to_csv('final_queries.csv')

df = pd.read_csv('final_queries.csv')
#print(df.head())

leaf_counts = df.groupby('category').count().reset_index().sort_values(by='query').reset_index(drop=True)
print(leaf_counts)
smallest_n_queries = leaf_counts.loc[0, 'query']
while smallest_n_queries <= min_queries:
    smallest_category = leaf_counts.loc[0, 'category']
    smallest_n_queries = leaf_counts.loc[0, 'query']
    print("smallest category: ", smallest_category)
    print("smallest n queries: ", smallest_n_queries)
    # rolled_up_dict[leaf_counts.loc[0, 'category']] = parents_dict[row['category']]
    # df = df.where(df[df.category==smallest_category], parents_dict[leaf_counts.loc[0, 'category']])
    df['category'].replace(smallest_category, parents_df[parents_df['category'] == smallest_category]['parent'].values[0], inplace=True)
    leaf_counts = df.groupby('category').count().reset_index().sort_values(by='query').reset_index(drop=True)
    print(leaf_counts)


print("NUM CATEGORIES: ", len(set(df.category)))


#rollback_ancestors(df)


# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
