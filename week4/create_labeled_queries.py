import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv

# for normalize query
import string
import nltk
nltk.download('punkt')
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
stemmer = SnowballStemmer('english')

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=100,  help="The minimum number of queries per category label (default is 1)")
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
# I did the same processing in extract_titles in week3
def normalize_query(query):
    query = query.replace('\n', ' ')
    query = query.lower()
    query = query.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
    # words = word_tokenize(query)
    # words = [stemmer.stem(word) for word in words]    
    # query = word_tokenize(query)
    # query = " ".join(words)
    #print ("normalized query: " + query)
    return query

# DF with cat count
df_cat_counts = df.groupby('category').size().reset_index(name='count')
print(df_cat_counts.loc[[0]])

print("first query in df  " + df['query'].values[0])
# apply query normalization to every query in Df
df['query'] = df['query'].apply(normalize_query)
print("Normalized first query in df " + df['query'].values[0])
print(" Total unique Categories: ", len(df['category'].unique()))


df_with_cat_counts = df.groupby('category').size().reset_index(name='count')
df_with_cat_counts_parents_merged = df.merge(df_with_cat_counts, how='left', on='category').merge(parents_df, how='left', on='category')
while len(df_with_cat_counts_parents_merged[df_with_cat_counts_parents_merged['count'] < min_queries]) > 0:
    df_with_cat_counts_parents_merged.loc[df_with_cat_counts_parents_merged['count'] < min_queries, 'category'] = df_with_cat_counts_parents_merged['parent']
    df = df_with_cat_counts_parents_merged[['category', 'query']]
    df = df[df['category'].isin(categories)]
    df_with_cat_counts = df.groupby('category').size().reset_index(name='count')
    df_with_cat_counts_parents_merged = df.merge(df_with_cat_counts, how='left', on='category').merge(parents_df, how='left', on='category')



# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
print(" Post Process: Total unique Categories: ", len(df['category'].unique()))
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
