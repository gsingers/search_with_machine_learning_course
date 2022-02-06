import os
import argparse
from pathlib import Path

def transform_training_data(title, comment):
    # IMPLEMENT
    return title + ' ' + comment



parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to")
general.add_argument("--min_product_names", default=5, type=int, help="the file to output to")
general.add_argument("--max_product_names", default=50, type=int, help="the file to output to")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)


# Directory for review data
directory = r'/workspace/datasets/product_data/reviews/'

print("Writing results to %s" % output_file)
with open(output_file, 'w') as output:
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            with open(os.path.join(directory, filename)) as xml_file:
                for line in xml_file:
                    if '<rating>'in line:
                        rating = line[12:15]
                    elif '<title>' in line:
                        title = line[11:len(line) - 9]
                    elif '<comment>' in line:
                        comment = line[13:len(line) - 11]
                    elif '</review>'in line:
                      output.write("__label__%s %s\n" % (rating, transform_training_data(title, comment)))
