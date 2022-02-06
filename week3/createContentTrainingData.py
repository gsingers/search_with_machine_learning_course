import argparse
import os
import xml.etree.ElementTree as ET
from pathlib import Path
# Directory for product data

def transform_name(product_name):
    # IMPLEMENT
    return product_name

directory = r'/workspace/datasets/product_data/products/'
parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--min_product_names", default=5, type=int, help="The minimum number of products per category.")
general.add_argument("--max_product_names", default=50, type=int, help="The maximum number of products per category.")
args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

# IMPLEMENT:  Track the number of items in each category and only output if above the min and below the max
min_product_names = args.min_product_names
max_product_names = args.max_product_names

print("Writing results to %s" % output_file)
with open(output_file, 'w') as output:
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            print("Processing %s" % filename)
            f = os.path.join(directory, filename)
            tree = ET.parse(f)
            root = tree.getroot()
            for child in root:
                # Check to make sure category name is valid
                if (child.find('name') is not None and child.find('name').text is not None and
                    child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and
                    child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None):
                      # Choose last element in categoryPath as the leaf categoryId
                      cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
                      # Replace newline chars with spaces so fastText doesn't complain
                      name = child.find('name').text.replace('\n', ' ')

                      output.write("__label__%s %s\n" % (cat, transform_name(name)))
