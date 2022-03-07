import argparse
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from nltk.stem import SnowballStemmer
import pandas as pd
from sklearn.model_selection import train_test_split

stemmer = SnowballStemmer("english")

def transform_name(product_name):
    # replace punctuation with spaces
    # credit: https://stackoverflow.com/a/34922745/158328
    clean = re.sub(r"[(),:.;@#?!&$/\"-]+\ *", " ", product_name)
    clean = re.sub(r"[ ]+", " ", clean)
    clean_lc = clean.lower()
    stemmed = " ".join([stemmer.stem(word) for word in clean_lc.split()])
    if stemmed == "":
        print("Empty stemmed sequence detected")
        exit(1)
    # lowercase
    return stemmed

# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output_punct_to_space_lc.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")
general.add_argument("--train_test_ratio", default=0.1, type=float, help="Train / test ratio: if set it 0.1, 10% goes to test, 90% goes to train")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
min_products = args.min_products
sample_rate = args.sample_rate
train_test_ratio = args.train_test_ratio

df = pd.DataFrame(columns=['category', 'product'])

print("Writing results to %s" % output_file)
with open(output_file, 'w') as output:
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            print("Processing %s" % filename)
            f = os.path.join(directory, filename)
            tree = ET.parse(f)
            root = tree.getroot()
            for child in root:
                if random.random() > sample_rate:
                    continue
                # Check to make sure category name is valid
                if (child.find('name') is not None and child.find('name').text is not None and
                    child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
                    child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None):
                      # Choose last element in categoryPath as the leaf categoryId
                      cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
                      # Replace newline chars with spaces so fastText doesn't complain
                      name = child.find('name').text.replace('\n', ' ')
                      #df = df.append({'category': cat, 'product': name}, ignore_index=True)
                      dfi = pd.DataFrame({'category': [cat], 'product': [name]})
                      df = pd.concat([df, dfi], ignore_index=True, axis=0)
                      #output.write("__label__%s %s\n" % (cat, transform_name(name)))
    # filter out
    print(f"Filtering out by category frequency and min_products={min_products}")
    filtered = df.groupby("category").filter(lambda x: len(x) > min_products)
    print(f"Saving to output file {output_file}")
    # shuffle and create train / test splits
    print("Shuffling dataset")
    shuffled = filtered.sample(frac=1).reset_index(drop=True)  # shuffle things
    print(f"Train/test split with ratio of {train_test_ratio}")
    train, test = train_test_split(shuffled, test_size=train_test_ratio)
    for i, row in shuffled.iterrows():
        cat = row["category"]
        name = row["product"]
        output.write("__label__%s %s\n" % (cat, transform_name(name)))
    # save train and test
    print("Saving train and test splits")
    with open(output_file+".train", 'w') as train_output:
        for i, row in train.iterrows():
            cat = row["category"]
            name = row["product"]
            train_output.write("__label__%s %s\n" % (cat, transform_name(name)))

    with open(output_file+".test", 'w') as test_output:
        for i, row in test.iterrows():
            cat = row["category"]
            name = row["product"]
            test_output.write("__label__%s %s\n" % (cat, transform_name(name)))