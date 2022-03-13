# %%
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import csv
from pathlib import Path
from tqdm.auto import tqdm

tqdm.pandas()


# %%
categories_file_name = "/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml"
query_df_filename = "/workspace/datasets/week4/query_df.pk"

output_dir = "/workspace/datasets/week4/"
min_queries = 100

# %%
parser = argparse.ArgumentParser(description="Process arguments.")
general = parser.add_argument_group("general")
general.add_argument(
    "--min_queries",
    default=1,
    help="The minimum number of queries per category label (default is 1)",
)

# %%
args = parser.parse_args()
if args.min_queries:
    min_queries = int(args.min_queries)

# %%
# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = "cat00000"
tree = ET.parse(categories_file_name)
root = tree.getroot()
# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
names = []
paths = []
parents = []
for child in root:
    id = child.findtext("id")
    cat_path = child.find("path")
    cat_path_ids = [cat.findtext("id") for cat in cat_path]
    cat_path_names = [cat.findtext("name") for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        names.append(cat_path_names[-1])
        paths.append(" > ".join(reversed(cat_path_names)))
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(
    {
        "category": categories,
        "parent": parents,
        "name": names,
        "path": paths,
    },
)
parents_df = parents_df.set_index("category", drop=False)
assert parents_df.index.is_unique

# %%
# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_pickle(query_df_filename)
df = df[df.category.isin(categories)]
print(f"df: len={len(df)} columns={df.columns.to_list()}")
print(df.iloc[:5].to_string())
tdf = df.assign(orig_category=df.category)


# %%
tdf.category = tdf.orig_category
parents_df = parents_df.set_index("category", drop=False)
while True:
    vc = tdf.category.value_counts()
    small_cats = vc[vc < min_queries].index.to_series()
    small_cats_parents = small_cats.map(parents_df.parent)
    # Pick only leaf categories in one iteration ignoring non-leaf.
    # It is non-leaf if it is also in parents, so remove it.
    cats_to_filter = small_cats[~small_cats.isin(small_cats_parents)]

    print(f"\nNo. of unique categories = {len(vc)}")
    print(f"No. of categories with #queries < {min_queries} = {len(cats_to_filter)} (leaf) / {len(small_cats)} (all)")
    # print(cats_to_filter.map(parents_df.path).sort_values().to_string())

    if len(cats_to_filter) == 0:
        break

    mask = tdf.category.isin(cats_to_filter)
    updated_cats = tdf.category[mask].map(parents_df.parent)
    tdf.update(updated_cats)

    print(f"No. of affected rows = {len(updated_cats)}")
    # print(tdf.loc[mask, []].assign(
    #     q = tdf["query"].str[:20],
    #     orig_path = tdf.orig_category.map(parents_df.path.str[:30]),
    #     new_name = tdf.category.map(parents_df.name),
    # ).to_markdown(index=False))


# %%
# Make sure that every category is in the taxonomy.
tdf = tdf[tdf.category.isin(categories)]
# Create labels in fastText format.
lines = "__label__" + tdf["category"] + " " + tdf["query"]
# Shuffle
lines = lines.sample(frac=1, random_state=42)
# Create test and train set
def to_txt(df, filepath):
    print(f"Writing {len(df)} lines to {filepath}")
    df.to_csv(
        str(filepath),
        header=False,
        sep="|",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
        index=False,
    )


print()
output_fp = Path(output_dir) / f"labeled_data.mq{min_queries}.txt"
train_fp = Path(output_dir) / f"train.mq{min_queries}.txt"
test_fp = Path(output_dir) / f"test.mq{min_queries}.txt"
to_txt(lines, output_fp)
to_txt(lines[:50000], train_fp)
to_txt(lines[-50000:], test_fp)
