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

TRAINING_DATA_SIZE = 200000

stopwords = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is",
             "it", "no", "not", "of", "on", "or", "such", "that", "the", "their", "then", "there",
             "these", "they", "this", "to", "was", "will", "with"]

stemmer = nltk.stem.SnowballStemmer('english', ignore_stopwords=True)

categories_file_name = r'../data/categories_0001_abcat0010000_to_pcmcat99300050000.xml'
queries_file_name = r'../data/train.csv'

# The root category, named Best Buy with id cat00000, doesn't have a parent.
ROOT_CATEGORY_ID = 'cat00000'


def keep_word(word):
    return word not in stopwords and len(word) > 2


def transform_queries(query: str) -> str:
    query_transformed = query.lower()
    words = nltk.word_tokenize(query_transformed)

    words = [w.strip() for w in words if keep_word(w)]
    words = [stemmer.stem(word) for word in words]
    words = [re.sub("[^a-zA-Z0-9]+", " ", w) for w in words if w]
    words = [w.strip() for w in words if w.strip()]
    # normalize additionally by sorting alphabetically
    words = sorted(words)
    query_transformed = ' '.join(words)
    # print(f'old query: {query}, transformed: {query_transformed}')
    return query_transformed.strip()


def transform_queries2(query: str) -> str:
    query_transformed = query.lower()
    words = nltk.word_tokenize(query_transformed)

    words = [w.strip() for w in words if keep_word(w)]
    # don't stem this time just remove s
    words = [word.removesuffix('s') for word in words]
    # this time remove also numbers
    words = [re.sub("[^a-zA-Z]+", " ", w) for w in words if w]
    words = [w.strip() for w in words if w.strip()]
    # don't sort this time
    # words = sorted(words)
    query_transformed = ' '.join(words)
    return query_transformed.strip()


def get_parents_df() -> pd.DataFrame:
    tree = ET.parse(categories_file_name)
    root = tree.getroot()
    categories = []
    parents = []
    for child in root:
        cat_path: Element = child.find('path')
        cat_path_ids: List[str] = [cat.find('id').text for cat in cat_path]
        leaf_id = cat_path_ids[-1]
        if leaf_id != ROOT_CATEGORY_ID:
            categories.append(leaf_id)
            parents.append(cat_path_ids[-2])
    parents_df = pd.DataFrame(list(zip(categories, parents)), columns=['category', 'parent'])

    return parents_df


def read_and_transform_training_data():
    df = pd.read_csv(queries_file_name)[['category', 'query']]
    categories: List['str'] = df['category'].tolist()
    df['query'] = df['query'].apply(transform_queries2)
    print(df.head())
    print(len(df))
    df.to_csv('transformed_queries2.csv')
    return df


def save_training_data(parents_df: pd.DataFrame, queries_df: pd.DataFrame, min_queries) -> pd.DataFrame:
    assert all(parents_df.columns == pd.Index(['category', 'parent']))
    assert all(queries_df.columns == pd.Index(['category', 'query']))

    queries_df = queries_df[queries_df['category'].isin(parents_df['category'])]
    # Roll up categories to ancestors to satisfy the minimum number of queries per category.
    categories = reduce_categories(min_queries, parents_df, queries_df)

    # Create labels in fastText format.
    queries_df['label'] = '__label__' + queries_df['category']
    # Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
    queries_df = queries_df.dropna()
    number_unique_categories = len(queries_df['category'].unique())
    print(f'{number_unique_categories} unique categories for min queries parameter {min_queries}')

    # random shuffle
    queries_df = queries_df.sample(frac=1, random_state=min_queries)

    queries_df['output'] = queries_df['label'] + ' ' + queries_df['query']
    # queries_df[['output']].to_csv(f'labeled_query_data_{min_queries}.txt', header=False, sep='|', escapechar='\\',
    #                               quoting=csv.QUOTE_NONE,
    #                               index=False)

    training_data = queries_df[['output']].head(TRAINING_DATA_SIZE)
    training_data.to_csv(f'queries_train_{min_queries}', header=False, sep='|', escapechar='\\',
                         quoting=csv.QUOTE_NONE,
                         index=False)
    testing_data = queries_df[['output']].tail(20000)
    testing_data.to_csv(f'queries_test_{min_queries}', header=False, sep='|', escapechar='\\',
                        quoting=csv.QUOTE_NONE,
                        index=False)


def reduce_categories(min_queries: int, parents_df: pd.DataFrame, queries_df: pd.DataFrame) -> pd.DataFrame:
    while True:
        number_of_queries_per_category: pd.Series = queries_df.groupby('category').size()
        print(number_of_queries_per_category.size)
        categories_with_too_few_queries = number_of_queries_per_category[
            number_of_queries_per_category < min_queries].index.tolist()
        print(f'got {len(categories_with_too_few_queries)} categories to replace')
        if len(categories_with_too_few_queries) == 0:
            return queries_df
        for category in categories_with_too_few_queries:
            if not category or category == 'None':
                continue
            parent_category_found = parents_df[parents_df["category"] == category]['parent']
            if not parent_category_found.empty:
                parent_category = parent_category_found.iloc[0]
                queries_df['category'] = queries_df['category'].replace(category, parent_category)
            else:
                print(category)


if __name__ == '__main__':
    parents_df = get_parents_df()

    # df = read_and_transform_training_data()

    queries_df = pd.read_csv('transformed_queries2.csv', header=0)[['category', 'query']]
    print(len(queries_df))
    for min_queries in [50, 100, 500, 1000, 2000, 5000]:
        save_training_data(parents_df, queries_df, min_queries=min_queries)
