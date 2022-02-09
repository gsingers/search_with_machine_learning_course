import os
import xml.etree.ElementTree as ET

def transform_training_data(name):
    # IMPLEMENT
    return name.replace('\n', ' ')

# Directory for product data
directory = r'/workspace/datasets/product_data/products/'

for filename in os.listdir(directory):
    if filename.endswith(".xml"):
        f = os.path.join(directory, filename)
        tree = ET.parse(f)
        root = tree.getroot()
        for child in root:
            if (child.find('name') is not None and child.find('name').text is not None):
                name = transform_training_data(child.find('name').text)
                print(name)
