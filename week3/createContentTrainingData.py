import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
from nltk import word_tokenize
from nltk.downloader import Downloader
from nltk.stem import SnowballStemmer


RANDOM_STATE = 42

STEMMER_DEPENDENCY = "punkt"
if not Downloader().is_installed(STEMMER_DEPENDENCY):
    Downloader().download(STEMMER_DEPENDENCY)
    assert Downloader().is_installed(STEMMER_DEPENDENCY)

stemmer = SnowballStemmer("english")


def transform_name(product_name):
    # DONE: IMPLEMENT
    # return product_name
    # Remove punctuation, numbers, etc., lowercase, and stem tokens
    tokens = word_tokenize(product_name)
    tokens = (stemmer.stem(word.lower()) for word in tokens if word.isalpha())
    product_name_normalized = " ".join(tokens)
    return product_name_normalized


# Directory for product data
directory = r"/workspace/search_with_machine_learning_course/data/pruned_products/"

parser = argparse.ArgumentParser(description="Process some integers.")
general = parser.add_argument_group("general")
general.add_argument(
    "--input", default=directory, help="The directory containing product data"
)
general.add_argument(
    "--output",
    default="/workspace/datasets/fasttext/output.fasttext",
    help="the file to output to",
)

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument(
    "--sample_rate",
    default=1.0,
    type=float,
    help="The rate at which to sample input (default is 1.0)",
)

# DONE: IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument(
    "--min_products",
    default=0,
    type=int,
    help="The minimum number of products per category (default is 0).",
)

general.add_argument(
    "--shuffle",
    action=argparse.BooleanOptionalAction,
    help="Shuffle the data or not (default is False).",
)

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
    os.mkdir(output_dir)

if args.input:
    directory = args.input
# DONE: IMPLEMENT:  Track the number of items in each category and only output if above the min
df = pd.DataFrame({"cat": [], "name": []})
min_products = args.min_products
sample_rate = args.sample_rate
shuffle = args.shuffle

# print("Writing results to %s" % output_file)
# with open(output_file, "w") as output:
for filename in os.listdir(directory):
    if filename.endswith(".xml"):
        print(f"Processing {filename}")
        f = os.path.join(directory, filename)
        tree = ET.parse(f)
        root = tree.getroot()
        for child in root:
            if random.random() > sample_rate:
                continue
            # Check to make sure category name is valid
            if (
                child.find("name") is not None
                and child.find("name").text is not None
                and child.find("categoryPath") is not None
                and len(child.find("categoryPath")) > 0
                and child.find("categoryPath")[len(child.find("categoryPath")) - 1][
                    0
                ].text
                is not None
            ):
                # Choose last element in categoryPath as the leaf categoryId
                cat = child.find("categoryPath")[
                    len(child.find("categoryPath")) - 1
                ][0].text
                # Replace newline chars with spaces so fastText doesn't complain
                name = child.find("name").text.replace("\n", " ")
                # output.write("__label__%s %s\n" % (cat, transform_name(name)))
                df.loc[len(df)] = [cat, transform_name(name)]


# Filter data based on min_products
def get_categories_to_keep(df, min_products):
    df_category_counts = df["cat"].value_counts()
    return set(df_category_counts[df_category_counts >= min_products].index)

if min_products > 0 :
    categories_to_keep = get_categories_to_keep(df, min_products)
    df = df[df["cat"].isin(categories_to_keep)]

if shuffle:
    df = df.sample(frac=1, random_state=RANDOM_STATE)

print(f"Writing results to {output_file}")
with open(output_file, "w") as output:
    for index, row in df.iterrows():
        cat = row['cat']
        name = row['name']
        output_str = f"__label__{cat} {name}\n"
        output.write(output_str)
