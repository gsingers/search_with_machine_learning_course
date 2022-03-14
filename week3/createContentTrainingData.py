import argparse
import collections
import logging
import os
import random
import string
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import nltk
from nltk.stem.snowball import EnglishStemmer
from nltk.tokenize import word_tokenize


trans_table = str.maketrans('', '', string.punctuation)
stemmer = EnglishStemmer(ignore_stopwords=True)
logger = logging.getLogger(__name__)

Product = collections.namedtuple("Product", ["category", "name"])


def remove_punkt(tokens):
    for token in tokens:
        t = token.translate(trans_table)
        if t:
            yield t


def stem(tokens):
    yield from map(stemmer.stem, tokens)


token_filters = [
    remove_punkt,
    stem
]

def transform_name(product_name):
    normalized = unicodedata.normalize("NFKD", product_name).encode("ascii", "ignore").decode("utf-8")
    tokens = word_tokenize(normalized)
    for tf in token_filters:
        tokens = tf(tokens)
    return " ".join(tokens)


def iter_product_elems(directory):
    for filename in os.listdir(directory):
        logger.debug("Processing %s", filename)
        if filename.endswith(".xml"):
            filepath = os.path.join(directory, filename)
            for _, elem in ET.iterparse(filepath):
                if elem.tag == "product":
                    yield elem


def sample(iterable, rate):
    assert 0 <= rate <= 1
    if rate == 1:
        yield from iterable
    for elem in iterable:
        if random.random() <= rate:
            yield elem


class ProductParser:
    def __init__(self, max_category_depth):
        self.max_category_depth = max_category_depth

    def parse(self, product_elem):
        category_path = product_elem.find("categoryPath")
        category_path_idx = min(self.max_category_depth, len(category_path)-1)
        return Product(
            category=category_path[category_path_idx].find("id").text,
            name=product_elem.find("name").text
        )


def filter_min_products(products, n):
    if n == 0:
        yield from products
    product_list = list(products)
    cnt = collections.Counter(product.category for product in product_list)
    for product in product_list:
        if cnt[product.category] >= n:
            yield product


# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

general.add_argument("--max-category-depth", default=-1, type=int, help="Cap category depth to n (default is -1, which equals to no cap)")


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    nltk.download(["punkt", "stopwords"])

    args = parser.parse_args()
    product_parser = ProductParser(args.max_category_depth)

    products = map(product_parser.parse, sample(iter_product_elems(args.input), rate=args.sample_rate))
    lines = [
        f"__label__{product.category} {transform_name(product.name)}\n"
        for product in filter_min_products(products, n=args.min_products)
    ]
    random.shuffle(lines)

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Writing results to %s", args.output)
    with path.open("w") as output:
        output.writelines(lines)
