import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv

# Useful if you want to perform stemming.
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk import sent_tokenize, word_tokenize

stemmer = nltk.stem.PorterStemmer()

def transform_query(query):
    tokens = word_tokenize(query)
    tokens = [word for word in tokens if (word.isalpha()) & (word not in stopwords.words('english'))]
    tokens = [word.lower() for word in tokens]
    tokens = [stemmer.stem(word) for word in tokens]
    transformed_query = " ".join(tokens)
    return transformed_query

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
print(parents_df.head())

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]
# make a subset of data
print("Shape:", df.shape)
df = df.iloc[:10_000]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
print(df.head())
df['query_filtered']=df['query'].apply(transform_query)
# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
# count number of categories
df["nb_queries"] = df.groupby('category')['query'].transform(len)

def get_parent(candidate:str):
    return parents_df[parents_df['category']  == candidate]['parent'].values[0]

# get parent for each cateogory
df['parent'] = df['category'].apply(get_parent) 

# create boolean mask
MIN_CUT = 100
df.loc[df['nb_queries'] < MIN_CUT, 'to_swap'] = 1
# apply boolean mask
print( df[['category','parent']].mask(df['to_swap']==1, df[['parent','category']].values[:, 0]).shape)
df[['category']] = df[['category','parent']].mask(df['to_swap']==1, df[['parent','category']].values[:, 0])
print(df.head(20))

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
