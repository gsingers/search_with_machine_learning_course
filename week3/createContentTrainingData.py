import argparse
import os
import string
import random
import xml.etree.ElementTree as ET
from pathlib import Path
import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from nltk.corpus import stopwords
import pandas as pd

def transform_name(product_name):
    product_name = product_name.lower()

    product_name = product_name.translate(str.maketrans('', '', string.punctuation))
    product_name = product_name.replace(u"\u2122", '').replace(u"\u00AE", '')

    snowball = SnowballStemmer("english")
    tokens = word_tokenize(product_name)
    tokens = [token for token in tokens if token not in stopwords.words('english')]
    tokens = [snowball.stem(token) for token in tokens]
    product_name = ' '.join(tokens)
    
    return product_name

# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/search_with_machine_learning_course/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")

# Setting max_depth takes the ancestor category max_depth times removed, in order to reduce classification granularity and gain precision.
general.add_argument("--max_depth", default=1, type=int, help="The degree of classification granularity, defined as an ascending number from the leaf to the root of the category path (default is 1 - the leaf category).")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
# Track the number of items in each category and only output if above the min
min_products = args.min_products
sample_rate = args.sample_rate
max_depth = args.max_depth

print("Writing results to %s" % output_file)
with open(output_file, 'w') as output:
    product_dict = {}
    product_dict['name'] = []  
    product_dict['category'] = [] 
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
                      cat = child.find('categoryPath')[len(child.find('categoryPath')) - max_depth][0].text
                      # Replace newline chars with spaces so fastText doesn't complain
                      name = child.find('name').text.replace('\n', ' ')
                      product_dict['name'].append(name)
                      product_dict['category'].append(cat)
    
    df = pd.DataFrame(product_dict)
    filtered = df.groupby('category')['name'].filter(lambda x: len(x) >= min_products)
    df = df[df['name'].isin(filtered)]
    print("{} products filtered".format(len(df)-len(filtered)))

    for _, row in df.iterrows():
        output.write("__label__%s %s\n" % (row['category'], row['name']))