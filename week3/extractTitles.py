import os
import random
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

directory = r'/workspace/search_with_machine_learning_course/data/pruned_products'
parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing the products")
general.add_argument("--output", default="/workspace/datasets/fasttext/titles.txt", help="the file to output to")

# Consuming all of the product data takes a while. But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=0.1, type=float, help="The rate at which to sample input (default is 0.1)")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input

sample_rate = args.sample_rate

import re
import string
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer(language='english')
_re_spec = re.compile(r'([/#\\-\\.:])')

def spec_add_spaces(t):
    "Add spaces around . : - / \ and #"
    return _re_spec.sub(r' \1 ', t)

# Causes the resulting RE to match from m to n repetitions of the preceding RE, attempting to match as many repetitions as possible.
_re_space = re.compile(' {2,}')

def rm_useless_spaces(t):
    "Remove multiple spaces"
    return _re_space.sub(' ', t)

def rm_punct(t):
    for p in string.punctuation:
        t = t.replace(p, ' ')
    return t

def transform_training_data(name):
    "Transform product name by replacing punctuations, removing multiple spaces, stemming, lower casing"

    # replace_punct
    name = spec_add_spaces(name)
    
    # remove punct
    name = rm_punct(name)
    
    # replace multiple spaces
    name = rm_useless_spaces(name)
    
    # fix registered, trademark, copyright symbol
    # remove non-ascii characters from name
    name = name.encode(encoding='ascii', errors='ignore').decode()
    
    # remove numeric
    name = ' '.join([o for o in name.split(' ') if not o.isnumeric()])
    
    # add stemmer
    name = stemmer.stem(name)
    
    # lower case
    name = name.lower()
    
    return name.replace('\n', ' ')

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
                    output.write(name + "\n")