import argparse
import os
import sys
import random
import xml.etree.ElementTree as ET
from pathlib import Path
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd


nltk.download("punkt")
en_stopwords=set(stopwords.words('english'))
############################
########category data
# Location for category data

cat_ancestor_at_depth =dict()

def populate_category_at_max_depth(max_depth):
    categoriesFilename = '/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'
    maxDepth = max_depth
    tree = ET.parse(categoriesFilename)
    root = tree.getroot()

    catPathStrs = set()

    for child in root:
        catPath = child.find('path')
        catId = child.find('id')
        depth = 0
        ancestorId = ''
        for cat in catPath:
            ancestorId = cat.find('id').text
            depth = depth + 1
            if maxDepth > 0 and depth == maxDepth:
                break
        cat_ancestor_at_depth.update({catId:ancestorId})
#############################

def find_and_substitute_with_ancestor(catId):
    if catId in cat_ancestor_at_depth:
        return cat_ancestor_at_depth[catId]
    else:
        return catId

def transform_name(product_name):
    # IMPLEMENT
    #convert to lower
    name = product_name.lower()
    stemmer = SnowballStemmer("english")
    name = stemmer.stem(name)
    words = nltk.word_tokenize(name)
    new_words= [word for word in words if word.isalnum()]
    new_words = [word for word in new_words if word not in en_stopwords]
    product_name = ' '.join(new_words)
    return product_name

# Directory for product data
directory = r'/workspace/search_with_machine_learning_course/data/pruned_products/'

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing product data")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")

# Consuming all of the product data will take over an hour! But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=1.0, type=float, help="The rate at which to sample input (default is 1.0)")

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")


general.add_argument("--max_depth", default=0, type=int, help="optional arg to specify max depth of category tree")


args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input
# IMPLEMENT:  Track the number of items in each category and only output if above the min
min_products = args.min_products
sample_rate = args.sample_rate
maxDepth = args.max_depth
populate_category_at_max_depth(maxDepth)

col_cat_label = "catlabel"
col_name = "name"
col_names = [col_cat_label,col_name]
df = pd.DataFrame(columns=col_names)

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
                      row = {col_cat_label:cat,col_name:name}
                      df = df.append(row,ignore_index=True)
                      #output.write("__label__%s %s\n" % (cat, transform_name(name)))


    #print(df.head())
    print("df size {}".format(df.count))
    #print(df.groupby(col_cat_label).count())
    filtered_df = df.groupby(col_cat_label).filter(lambda x: x[col_cat_label].count() > min_products)
    #print("filtered df size{}".format(filtered_df.count))
    filtered_df.apply(lambda row: output.write("__label__%s %s\n" % (find_and_substitute_with_ancestor(row[col_cat_label]), transform_name(row[col_name]))), axis=1)