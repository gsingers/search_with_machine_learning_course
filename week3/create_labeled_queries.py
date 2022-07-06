import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
import re

import logging
FORMAT = "%(name)s -- %(asctime)s -- %(message)s"
LOGGER = logging.getLogger(__name__)
logging.basicConfig(format=FORMAT)
LOGGER.setLevel(logging.INFO)

# Useful if you want to perform stemming.
import nltk
stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data.txt'


def main(min_queries, output_file_name):
    # The root category, named Best Buy with id cat00000, doesn't have a parent.
    root_category_id = 'cat00000'

    tree = ET.parse(categories_file_name)
    root = tree.getroot()

    # Parse the category XML file to map each category id to its parent category id in a dataframe.
    LOGGER.info("Parsing category XML")
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
    parent_map = dict(zip(parents_df["category"], parents_df["parent"]))

    # Read the training data into pandas, only keeping queries with non-root categories in our category tree.
    LOGGER.info("Reading training data")
    df = pd.read_csv(queries_file_name)[['category', 'query']]
    df = df[df['category'].isin(categories)]
    df["parent"] = df["category"].map(parent_map)
    df["rolled_category"] = df["category"].copy()

    # IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
    def normalize_query(query):
        # remove nonalphanumeric characters and lowercase except for spaces and underscores
        norm_query = " ".join([x.lower() for x in query.split(" ") if x.isalnum()])
        # trim excess space
        norm_query = re.sub(' +', " ", norm_query)
        return norm_query

    LOGGER.info("Normalizing queries")
    df["normalized_query"] = df["query"].apply(normalize_query)

    # IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
    LOGGER.info("Pruning categories")
    def remap_categories(cat, remap_list):
        if cat in remap_list:
            return parent_map[cat]
        else:
            return cat

    acceptable = False
    while not acceptable:
        counter = df.groupby("rolled_category").agg({"normalized_query": "nunique"})
        counter = counter.rename(columns={"normalized_query": "nunique_queries"}).reset_index()
        low_count_categories = counter[counter["nunique_queries"] < min_queries]["rolled_category"].to_list()

        # remove root category if it appears
        if root_category_id in low_count_categories:
            low_count_categories.remove(root_category_id)

        if len(low_count_categories) == 0:
            LOGGER.info(f"All categories have at least {min_queries} unique queries")
            acceptable = True
        else:
            LOGGER.info(f"{len(low_count_categories)} categories with fewer than {min_queries} unique queries")
            df["rolled_category"] = df["rolled_category"].apply(remap_categories, remap_list=low_count_categories)

    # replace old category column with rolled up category column
    df = df.drop(columns=["category"])
    df = df.rename(columns={"rolled_category": "category"})

    # Create labels in fastText format.
    LOGGER.info("Creating labels")
    df['label'] = '__label__' + df['category']

    # Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
    df = df[df['category'].isin(categories)]
    LOGGER.info(f"Final category count: {len(set(df.category))}")

    LOGGER.info("Outputting data")
    df['output'] = df['label'] + ' ' + df['query']
    df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process arguments.')
    general = parser.add_argument_group("general")
    general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
    general.add_argument("--output", default=output_file_name, help="the file to output to")

    args = parser.parse_args()
    output_file_name = args.output

    if args.min_queries:
        min_queries = int(args.min_queries)

    main(min_queries, output_file_name)