import os
import random
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
import re

stopwords = [ "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is",
            "it", "no", "not", "of", "on", "or", "such", "that", "the", "their", "then", "there",
            "these", "they", "this", "to", "was", "will", "with"]

directory = r'/workspace/search_with_machine_learning_course/data/pruned_products'
parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing the products")
general.add_argument("--output", default="/workspace/datasets/fasttext/titles.txt", help="the file to output to")

# Consuming all of the product data takes a while. But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=0.2, type=float, help="The rate at which to sample input (default is 0.1)")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input

sample_rate = args.sample_rate

def keep_word(word):
    return word not in stopwords and len(word) > 2

def transform_training_data(name: str) -> str:
    
    product_name_transformed = name.lower()
    product_name_transformed =  re.sub("[^a-zA-Z]+", " ", product_name_transformed)
    
    words = product_name_transformed.split()
    #words = [w[0:-1] if w.endswith('s') else w for w in words]
    words = [w.strip() for w in words if keep_word(w)]
    product_name_transformed = ' '.join(words) 
    return product_name_transformed.strip()

# Directory for product data

print("Writing results to %s" % output_file)
with open(output_file, 'w') as output:
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            f = os.path.join(directory, filename)
            tree = ET.parse(f)
            root = tree.getroot()
            for child in root:
                if random.random() > sample_rate:
                    continue
                if (child.find('name') is not None and child.find('name').text is not None):
                    name = transform_training_data(child.find('name').text)
                    if name:
                        output.write(name + "\n")
