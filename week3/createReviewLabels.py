import os

directory = r'/workspace/datasets/bbuy/product_data/reviews/'

rating = ''
title = ''
comment = ''

for filename in os.listdir(directory):
    if filename.endswith('.xml'):
        with open(os.path.join(directory, filename)) as xml_file:
            for line in xml_file:
                if '<rating>'in line:
                    rating = line[12:15]
                elif 'title' in line:
                    title = line[11:len(line) - 9]
                elif 'comment' in line:
                    comment = line[13:len(line) - 11]
                elif '</review>'in line and rating != '' and title != '' and comment != '':
                    print ('__label__' + rating + ' ' + title + ' ' + comment)
                    rating = ''
                    title = ''
                    comment = ''
