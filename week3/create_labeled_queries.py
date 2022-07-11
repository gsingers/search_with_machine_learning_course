import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
from nltk.stem import SnowballStemmer
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from tqdm import tqdm

# Useful if you want to perform stemming.
import nltk
stemmer = SnowballStemmer("english")

nltk.download('punkt')
nltk.download('stopwords')

def normalize(query):
    special_tokens = ['\'','"','\u00A9','\u2122','\u00AE', '-', '.']
    tokens = word_tokenize(query)
    tokens = [token.lower() for token in tokens]
    tokens = [stemmer.stem(token) for token in tokens if not token in stopwords.words("english")]
    final_str = ' '.join(tokens)
    for special_token in special_tokens:
        final_str = final_str.replace(special_token, '')
    return final_str

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1000,  help="The minimum number of queries per category label (default is 1)")
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
print("parsing xml")
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
print("loading to pandas")
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
print("normalizing")
tqdm.pandas()
df['query'] = df['query'].progress_apply(lambda x: normalize(x))

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
print("rolling up")
parents_lookup = dict(zip(parents_df.category, parents_df.parent))
parents_lookup[root_category_id] = root_category_id

while True:
    grouped = df.groupby('category').count().reset_index()[['category', 'query']]
    grouped.columns = ['category', 'num']
    remaining_categories = set(grouped[grouped.num < min_queries].category.values)
    if not remaining_categories:
        break

    rolled = {
        c: (c if c not in remaining_categories else parents_lookup[c]) for c in grouped.category.values
    }
    df.category = df.category.apply(lambda c: rolled[c])

print(f'num_categories: {len(set(df.category.values))}')

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']

df = df.sample(frac=1).reset_index(drop=True)
df_train = df.head(50000)
df_test = df.tail(10000)

df_train[['output']].to_csv(f"{output_file_name}_train.txt", header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
df_test[['output']].to_csv(f"{output_file_name}_test.txt", header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)

df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
