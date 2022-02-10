import sys
import os
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

# Location for category data                                                                                                                                                               
categoriesFilename = '/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'
parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=categoriesFilename,  help="The full path to the filename containing the categories")
general.add_argument("--max_depth", default=0, type=int, help="the file to output to")

args = parser.parse_args()

categoriesFilename = args.input

# Optional arg to specify max depth of category tree
maxDepth = args.max_depth

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
