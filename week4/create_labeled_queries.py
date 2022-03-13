import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
# Useful if you want to perform stemming.
import nltk
from nltk.stem import SnowballStemmer
nltk.download("punkt")
from nltk.tokenize import word_tokenize
import string

#stemmer = nltk.stem.PorterStemmer()
stemmer = SnowballStemmer("english")

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

# IMPLEMENTED: Convert queries to lowercase, and optionally implement other normalization, like stemming.
#From week 3 exercise
def transform_name(product_name):
    # Transforming the name strings to lowercase, changing punctuation characters  
    # to spaces, and stemming (you can use the NLTK Snowball stemmer)
    spaceString=" "
    product_name.lower()
    for x in string.punctuation:
        product_name=product_name.replace(x,spaceString)
    stemmer = SnowballStemmer("english")
    transformed_product_name = " ".join((stemmer.stem(w) for w in word_tokenize(product_name)))
    return transformed_product_name

#From Daniel T's solution
def transform_query(query):
    # Transforming the name strings to lowercase, changing punctuation characters  
    # to spaces, and stemming (you can use the NLTK Snowball stemmer)
   ret = query.lower()
   ret = ''.join(c for c in ret if c.isalpha() or c.isnumeric() or c=='-' or c==' ' or c =='.')
   ret = ' '.join(map(stemmer.stem, ret.split(' ')))
   return ret

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
#TODO:for debug , remove later
print("Data from Parent: {}\n",parents_df.head())

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
#deduce category groups to determine counts
category_group = df['category'].value_counts()[lambda x: x>min_queries].index.tolist()
df = df[df['category'].isin(category_group)]

#default code
#df = df[df['category'].isin(categories)]
df['transformed_query']=df['query'].apply(transform_query)

print("Data from transformed Query:  {}\n",df.head())

# count number of categories
df["number_of_queries"] = df.groupby('category')['query'].transform(len)

# IMPLEMENTING: Roll up categories to ancestors to satisfy the minimum number of queries per category.
#Join the transformed query_df with parent_df to combine everything in one dataframe
df = df.join(parents_df.set_index("category"), on="category")

df["parent_group"] = df.groupby("parent")["transformed_query"].transform(lambda x: len(set(x)))

df["cat_group"] = df.groupby("category")["transformed_query"].transform(lambda x: len(set(x)))

print("Data after grouping:  {}\n",df.head())

df.loc[df["parent_group"] < min_queries, "drop"] = 1

print("Unique categories : {}", df['category'].nunique())

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
