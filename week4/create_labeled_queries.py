import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv

# Useful if you want to perform stemming.
from nltk.stem import *

stemmer = PorterStemmer()

categories_file_name = r"/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml"

queries_file_name = r"/workspace/datasets/train.csv"
output_file_name = r"/workspace/datasets/labeled_query_data.txt"

parser = argparse.ArgumentParser(description="Process arguments.")
general = parser.add_argument_group("general")
general.add_argument(
    "--min_queries",
    default=1,
    help="The minimum number of queries per category label (default is 1)",
)
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = "cat00000"

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find("id").text
    cat_path = child.find("path")
    cat_path_ids = [cat.find("id").text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(
    list(zip(categories, parents)), columns=["category", "parent"]
)

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[["category", "query"]]
df = df[df["category"].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
def normalize_text(input_text, stemming=True):

    if stemming:
        input_text = stemmer.stem(input_text)

    # Only retain lowercase letters, digits and spaces
    processed = ''.join([i.lower() for i in input_text if (i.isalpha() or i.isnumeric() or i==' ')])

    # Removing multiple spaces in sequence
    processed = ' '.join(processed.split())
    
    return processed

df['query_normalized']= df['query'].apply(lambda x: normalize_text(x)) 

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
parent_lookup = {row[1]:row[2] for row in parents_df.itertuples()}

# Find out which categories don't make the min_queries criterium
total_categories = list(df[['category','query']]\
    .groupby('category')\
    .filter(lambda x: len(x) > 0)\
    .groupby('category')\
    .size().index)

# Find out which categories don't make the min_queries criterium
invalid_categories = list(df[['category','query']]\
    .groupby('category')\
    .filter(lambda x: (len(x) < min_queries))\
    .groupby('category')\
    .size().index)

print(f"There are {str(len(total_categories))} categories in total")
print(f"There are {str(len(invalid_categories))} categories that don't meet the min_queries criterion")

# Iterate and update category data with the parent, until all satisfy the min_queries condition
while len(invalid_categories)>0:
    for cat in invalid_categories:
        try:
            # print(f"Replacing {cat} with its ancestor {parent_lookup[cat]}")
            df.loc[df['category']==cat,:] = parent_lookup[cat]
        except KeyError as e:
            print(f'Cant replace {cat}')
            pass
    invalid_categories = list(df[['category','query_normalized']]\
        .groupby('category')\
        .filter(lambda x: len(x) < min_queries)\
        .groupby('category')\
        .size().index)

# Create labels in fastText format.
df["label"] = "__label__" + df["category"]

# Print out how many categories are left
end_categories = list(df[['category','query_normalized']]\
    .groupby('category')\
    .filter(lambda x: len(x) >= min_queries)\
    .groupby('category')\
    .size().index)

print(f'For a minimum of {min_queries}, the number of categories remaining is {str(len(end_categories))}')

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df["category"].isin(categories)]
df["output"] = df["label"] + " " + df["query_normalized"]
df[["output"]].to_csv(
    output_file_name,
    header=False,
    sep="|",
    escapechar="\\",
    quoting=csv.QUOTE_NONE,
    index=False,
)