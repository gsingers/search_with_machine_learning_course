import argparse
import multiprocessing
import glob
from tqdm import tqdm
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd


def transform_name(product_name):
    # IMPLEMENT
    return product_name


# Directory for product data
directory = r"/workspace/datasets/product_data/products/"

parser = argparse.ArgumentParser(description="Process some integers.")
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory, help="The directory containing product data")
general.add_argument(
    "--output", default="/workspace/datasets/fasttext/output.fasttext", help="the file to output to"
)
general.add_argument(
    "--label",
    default="id",
    help="id is default and needed for downsteam use, but name is helpful for debugging",
)

# IMPLEMENT: Setting min_products removes infrequent categories and makes the classifier's task easier.
general.add_argument(
    "--min_products", default=0, type=int, help="The minimum number of products per category (default is 0)."
)

args = parser.parse_args()
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
if args.label == "name":
    names_as_labels = True


def _label_filename(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    labels = []
    for child in root:
        # Check to make sure category name is valid and not in music or movies
        if (
            child.find("name") is not None
            and child.find("name").text is not None
            and child.find("categoryPath") is not None
            and len(child.find("categoryPath")) > 0
            and child.find("categoryPath")[len(child.find("categoryPath")) - 1][0].text is not None
            and child.find("categoryPath")[0][0].text == "cat00000"
            and child.find("categoryPath")[1][0].text != "abcat0600000"
        ):
            # Choose last element in categoryPath as the leaf categoryId or name
            if names_as_labels:
                cat = child.find("categoryPath")[len(child.find("categoryPath")) - 1][1].text.replace(
                    " ", "_"
                )
            else:
                cat = child.find("categoryPath")[len(child.find("categoryPath")) - 1][0].text
            # Replace newline chars with spaces so fastText doesn't complain
            name = child.find("name").text.replace("\n", " ")
            labels.append((cat, transform_name(name)))

    return labels


if __name__ == "__main__":
    files = glob.glob(f"{directory}/*.xml")
    with multiprocessing.Pool() as p:
        all_labels = tqdm(p.imap(_label_filename, files), total=len(files))
        # Filter categories with less than 50 products
        flat_list = [item for sublist in all_labels for item in sublist]
        all_labels = flat_list
        df = pd.DataFrame(all_labels, columns=["cat", "product_name"])
        tdf = df.groupby("cat").count().reset_index().rename(columns={"product_name": "cnt"})
        tdf = tdf[tdf.cnt > min_products]
        df = df.merge(tdf, how="inner", on="cat")
        print("Filtering categories with less than. : {} products".format(min_products))
        print("Unique categories : {}", df.cat.nunique())
        unique_categories = set(df.cat)
        all_labels = [(x, y) for (x, y) in all_labels if x in unique_categories]
        cnt = 0

        with open(output_file, "w") as output:
            for (cat, name) in all_labels:
                cnt += 1
                output.write(f"__label__{cat} {name}\n")
        # wi
        #     for label_list in all_labels:
        #         for (cat, name) in label_list:
        #             output.write(f'__label__{cat} {name}\n')
