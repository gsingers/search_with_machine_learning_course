import argparse
import os
from pathlib import Path
import pandas as pd

parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default="/workspace/datasets/fasttext/labeled_products.txt",
                     help="The file containing product label data")
general.add_argument("--output", default="/workspace/datasets/fasttext/pruned_labeled_products.txt",
                     help="the file to output to")

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument("--min_products", default=500, type=int,
                     help="The minimum number of products per category (default is 500).")

args = parser.parse_args()
input_file = args.input
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
    os.mkdir(output_dir)

if args.input:
    directory = args.input
# IMPLEMENT: Track the number of items in each category and only output if above the min
min_products = args.min_products
names_as_labels = False
if args.label == 'name':
    names_as_labels = True

if __name__ == '__main__':

    product_data = []
    with open(input_file) as f:
        lines = f.readlines()
    for line in lines:
        product_data.append(line.split(" ", 1))

    df = pd.DataFrame(product_data, columns=['Label', "Name"])

    df_pruned = df[df.groupby("Label")['Name'].transform('size') >= min_products]

    f = open(output_file, "w")

    for ind in df_pruned.index:
        f.write(df_pruned['Label'][ind] + " " + df_pruned['Name'][ind])
    f.close()