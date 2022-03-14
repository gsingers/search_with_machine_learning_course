import re
import csv
import argparse
from typing import List

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import pandas as pd

import nltk

# only once
# nltk.download('stopwords')
# nltk.download('punkt')
stemmer = nltk.stem.SnowballStemmer('english', ignore_stopwords=True)

categories_file_name = r'../data/categories_0001_abcat0010000_to_pcmcat99300050000.xml'
queries_file_name = r'../data/train.csv'
output_file_name = r'labeled_query_data.txt'

# The root category, named Best Buy with id cat00000, doesn't have a parent.
ROOT_CATEGORY_ID = 'cat00000'


def transform_queries(query: str) -> str:
    query_transformed = query.lower()
    words = nltk.word_tokenize(query_transformed)

    words = [w.strip() for w in words if len(w) > 2]
    words = [stemmer.stem(word) for word in words]
    words = [re.sub("[^a-zA-Z0-9]+", " ", w) for w in words if w]
    words = [w.strip() for w in words if w.strip()]
    # normalize additionally by sorting alphabetically
    words = sorted(words)
    query_transformed = ' '.join(words)
    # print(f'old query: {query}, transformed: {query_transformed}')
    return query_transformed.strip()


def get_parents_df() -> pd.DataFrame:
    tree = ET.parse(categories_file_name)
    root = tree.getroot()
    # Parse the category XML file to map each category id to its parent category id in a dataframe.
    categories = []
    parents = []
    for child in root:
        # ??? what is this variable for?
        category_id = child.find('id').text
        cat_path: Element = child.find('path')
        cat_path_ids: List[str] = [cat.find('id').text for cat in cat_path]
        leaf_id = cat_path_ids[-1]
        if leaf_id != ROOT_CATEGORY_ID:
            categories.append(leaf_id)
            parents.append(cat_path_ids[-2])
    parents_df = pd.DataFrame(list(zip(categories, parents)), columns=['category', 'parent'])

    return parents_df


def read_and_transform_training_data():
    # Read the training data into pandas, only keeping queries with non-root categories in our category tree.
    df = pd.read_csv(queries_file_name)[['category', 'query']]
    categories: List['str'] = df['category'].tolist()
    df['query'] = df['query'].apply(transform_queries)
    print(df.head())
    print(len(df))
    df.to_csv('transformed_queries.csv')
    return df


def save_training_data(parents_df: pd.DataFrame, queries_df: pd.DataFrame, min_queries=None) -> pd.DataFrame:
    assert all(parents_df.columns == pd.Index(['category', 'parent']))
    assert all(queries_df.columns == pd.Index(['category', 'query']))

    queries_df = queries_df[queries_df['category'].isin(parents_df['category'])]
    # Roll up categories to ancestors to satisfy the minimum number of queries per category.
    if min_queries:
        while True:
            number_of_queries_per_category: pd.Series = queries_df.groupby('category').size()
            print(number_of_queries_per_category.size)
            categories_with_too_few_queries = number_of_queries_per_category[number_of_queries_per_category < min_queries].index.tolist()
            print(f'got {len(categories_with_too_few_queries)} categories to replace')
            if len(categories_with_too_few_queries) == 0:
                break
            for category in categories_with_too_few_queries:
                if not category or category == 'None':
                    continue
                parent_category_found = parents_df[parents_df["category"] == category]['parent']
                if not parent_category_found.empty:
                    parent_category = parent_category_found.iloc[0]
                    queries_df['category'] = queries_df['category'].replace(category, parent_category)
                else:
                    print(category)

    # Create labels in fastText format.
    queries_df['label'] = '__label__' + queries_df['category']
    # Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
    queries_df = queries_df.dropna()
    # random shuffle
    queries_df = queries_df.sample(n=len(df), random_state=777)
    queries_df['output'] = queries_df['label'] + ' ' + queries_df['query']
    queries_df[['output']].to_csv(
        output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)


if __name__ == '__main__':
    parents_df = get_parents_df()
    #df = read_and_transform_training_data()

    queries_df = pd.read_csv('transformed_queries.csv', header=0)[['category', 'query']]
    print(len(queries_df))
    save_training_data(parents_df, queries_df, min_queries=100)
