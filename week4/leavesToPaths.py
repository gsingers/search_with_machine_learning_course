import sys
import os
import xml.etree.ElementTree as ET

# Location for category data                                                                                                                                                               
categoriesFilename = '/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

# Optional arg to specify max depth of category tree                                                                                                                                       
maxDepth = 0
if (len(sys.argv) >- 2):
    maxDepth = int(sys.argv[1])

tree = ET.parse(categoriesFilename)
root = tree.getroot()

catDict = {}

for child in root:
    catPath = child.find('path')
    leafCat = catPath[-1].find('id').text
    catPathStr = ''
    depth = 0
    for cat in catPath:
        if catPathStr != '':
            catPathStr = catPathStr + ' > '
        catPathStr = catPathStr + cat.find('name').text
        depth = depth + 1
        if maxDepth > 0 and depth == maxDepth:
            break
    catDict[leafCat] = catPathStr

for line in sys.stdin:
    cat = line.rstrip('\n')
    if cat in catDict:
        print(catDict[cat])
