import argparse
import os
import random
import xml.etree.ElementTree as ET
import string
from pathlib import Path
from nltk.stem.snowball import SnowballStemmer
import pandas as pd
import sys

def getCategoryHierarchy():
    # Location for category data
    categoriesFilename = '/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

    tree = ET.parse(categoriesFilename)
    root = tree.getroot()

    catPathStrs = set()

    for child in root:
        catPath = child.find('path')
        catPathStr = ''
        depth = 0
        for cat in catPath:
            if catPathStr != '':
                catPathStr = catPathStr + '>'
            catPathStr = catPathStr + cat.find('id').text
            depth = depth + 1
            catPathStrs.add(catPathStr)

    # Sort for readability
    data = {'hierarchy': sorted(catPathStrs)}
    return pd.DataFrame(data)

stemmer = SnowballStemmer("english")
def transform_name(product_name):
    product_name = product_name.lower()
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    product_name = product_name.translate(translator)
    product_name = ' '.join(product_name.split())
    product_name = stemmer.stem(product_name)
    return product_name

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

catHierarchyDF = getCategoryHierarchy()
print(catHierarchyDF)
data = {'cat':[], 'name':[]}
print("Reading data from directory %s" % directory)

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
                    catDF = catHierarchyDF[catHierarchyDF['hierarchy'].str.endswith(">" + cat)]
                    if len(catDF) == 0:
                        continue
                    hierarchyStr = catDF.iloc[0]["hierarchy"]
                    catCount = hierarchyStr.count('>')
                    if catCount >= 2:
                        firstInd = hierarchyStr.find(">") 
                        secondInd = hierarchyStr.find(">", firstInd + 1)
                        thirdInd = hierarchyStr.find(">", secondInd + 1)
                        cat = hierarchyStr[secondInd + 1] if thirdInd == -1 else hierarchyStr[secondInd + 1:thirdInd]

                    data["cat"].append(cat)
                    data["name"].append(transform_name(name))

productDF = pd.DataFrame(data)
catCountsDF = productDF.groupby(['cat']).size().reset_index(name='counts')
catWithMinProducts = catCountsDF[catCountsDF.counts > min_products]
productFilteredDF = pd.merge(productDF, catWithMinProducts, on=['cat'], how='inner')[["cat", "name"]]

print("All products: %d" % len(productDF))
print(len(catCountsDF))
print(len(catWithMinProducts))
print("Filteredproducts: %d" % len(productFilteredDF))
print("Writing results to %s" % output_file)

with open(output_file, 'w') as output:    
    productFilteredDF = productFilteredDF.reset_index()  # make sure indexes pair with number of rows
    for index, row in productFilteredDF.iterrows():
        output.write("__label__%s %s\n" % (row['cat'], row['name']))