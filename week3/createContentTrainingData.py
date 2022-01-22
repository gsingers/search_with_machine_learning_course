import os
import xml.etree.ElementTree as ET

# Directory for product data
directory = r'/workspace/datasets/product_data/products/'

for filename in os.listdir(directory):
    if filename.endswith(".xml"):
        f = os.path.join(directory, filename)
        tree = ET.parse(f)
        root = tree.getroot()
        for child in root:
            
            # Check to make sure category name is valid
            if (child.find('name') is not None and child.find('name').text is not None and \
                child.find('categoryPath') is not None and len(child.find('categoryPath')) > 0 and \
                child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None):
                
                  # Choose last element in categoryPath as the leaf categoryId
                  cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
                
                  # Replace newline chars with spaces so fastText doesn't complain
                  name = child.find('name').text.replace('\n', ' ')
                  print('__label__' + cat + " " + name)
