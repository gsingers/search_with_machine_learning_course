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

categories_file_name = (
    r"/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml"
)

queries_file_name = r"/workspace/datasets/train.csv"
output_file_name = r"/workspace/datasets/fasttext/labeled_queries.txt"

parser = argparse.ArgumentParser(description="Process arguments.")
general = parser.add_argument_group("general")
general.add_argument(
    "--min_queries", default=1, help="The minimum number of queries per category label (default is 1)"
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
parents_df = pd.DataFrame(list(zip(categories, parents)), columns=["category", "parent"])

pmap = dict(zip(list(parents_df.category), list(parents_df.parent)))
cnt = 0


def clean_text(text):
    global cnt
    cnt += 1
    if cnt % 10000 == 0:
        print("Processed : ", cnt)
    text = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)
    words = [stemmer.stem(word).strip() for word in text.split()]
    cleaned_text = " ".join(words)
    if text == "Beats By Dr. Dre- Monster Pro Over-the-Ear Headphones":
        print("Cleaning : {} : {}".format(text, cleaned_text))
    return cleaned_text


def get_parent_conditionally(cnt_map, current_category):
    if current_category == root_category_id:
        return root_category_id

    cnt = cnt_map[current_category]
    if cnt < min_queries:
        return pmap[current_category]
    else:
        return current_category


# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
queries_df = pd.read_csv(queries_file_name)[["category", "query"]]
queries_df = queries_df[queries_df["category"].isin(categories)]
# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
if os.path.exists("normalized_cleaned.csv"):
    print("File exists reading cleaned csv")
    queries_df = pd.read_csv("normalized_cleaned.csv", sep="|")
else:
    queries_df["query"] = queries_df["query"].apply(lambda x: clean_text(x))
    queries_df.to_csv("normalized_cleaned.csv", sep="|", escapechar="\\", quoting=csv.QUOTE_NONE, index=False)

# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
tmp = queries_df.groupby("category").count().reset_index().rename(columns={"query": "cnt"})
count_map = dict(zip(tmp.category, tmp.cnt))
while len(tmp[tmp.cnt < min_queries]) > 0:
    queries_df = queries_df.merge(tmp, how="inner", on="category")
    queries_df["category"] = queries_df["category"].apply(lambda x: get_parent_conditionally(count_map, x))
    queries_df = queries_df[["category", "query"]]
    tmp = queries_df.groupby("category").count().reset_index().rename(columns={"query": "cnt"})
    count_map = dict(zip(tmp.category, tmp.cnt))

# Create labels in fastText format.
queries_df["label"] = "__label__" + queries_df["category"]

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
queries_df = queries_df[queries_df["category"].isin(categories)]
queries_df["output"] = queries_df["label"] + " " + queries_df["query"]
queries_df = queries_df[~queries_df["query"].isna()]
queries_df[["output"]].to_csv(
    output_file_name, header=False, sep="|", escapechar="\\", quoting=csv.QUOTE_NONE, index=False
)
