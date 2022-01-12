import os
import xml.etree.ElementTree as ET

directory = r'/workspace/datasets/bbuy/product_data/products/'
min_count = 1000
max_count = 1000

counts = {}
data = []

for filename in os.listdir(directory):
    if filename.endswith(".xml"):
        f = os.path.join(directory, filename)
        tree = ET.parse(f)
        root = tree.getroot()
        for child in root:
            if (child.find('name') is not None and \
                child.find('name').text is not None and \
                child.find('categoryPath') is not None and \
                len(child.find('categoryPath')) > 0 and \
                child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text is not None):
                  cat = child.find('categoryPath')[len(child.find('categoryPath')) - 1][0].text
                  if cat not in counts:
                      counts[cat] = 0
                  if counts[cat] < max_count:
                      name = child.find('name').text.replace('\n', ' ')
                      data.append((cat, name))
                      counts[cat] = counts[cat] + 1

for entry in data:
    if counts[entry[0]] >= min_count:
        print('__label__' + entry[0] + " " + entry[1])
