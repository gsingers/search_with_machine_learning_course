import os
import xml.etree.ElementTree as ET
import csv

directory = r'/workspace/datasets/'
categoriesFilename = directory + 'product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

tree = ET.parse(categoriesFilename)
root = tree.getroot()

parents = {}
catsToQueries = {}

for child in root:
    id = child.find('id').text
    catPath = child.find('path')
    catPathIds = []
    for cat in catPath:
        catPathIds.append(cat.find('id').text)
    if len(catPathIds) > 1:
        parents[id] = catPathIds[-2]
    else:
        parents[id] = ''
    catsToQueries[id] = set()

trainFilename = directory + 'train.csv'
minQueries = 10000

with open(trainFilename) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row[0] == 'user':
            continue
        catId = row[2]
        if catId not in catsToQueries:
            continue
        query = row[3].lower()
        catsToQueries[catId].add(query)

while len([cat for cat in catsToQueries if len(catsToQueries[cat]) < minQueries]) > 0:
    belowMinCats = set([cat for cat in catsToQueries if len(catsToQueries[cat]) < minQueries])
    parentsOfBelowMinCats = set([parents[cat] for cat in belowMinCats])
    belowMinCats = belowMinCats.difference(parentsOfBelowMinCats)
    for cat in belowMinCats:
        parent = parents[cat]
        if (parent not in catsToQueries):
            catsToQueries[parent] = set()
        for query in catsToQueries[cat]:
            catsToQueries[parent].add(query)
        del catsToQueries[cat]

for cat in catsToQueries:
    for query in catsToQueries[cat]:
        print('__label__' + cat + ' ' + query)
