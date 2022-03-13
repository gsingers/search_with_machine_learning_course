# %%
import pandas as pd
import fasttext
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import string
import nltk

# %%
categories_file = "/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml"
model_file = "/workspace/datasets/week4/model.mq100.e5.lr0.5.ng2.bin"
# File to store category id to name information
categories_df_file = "/workspace/datasets/week4/cats.pk"

# %%
def create_categories_df():
    categories = []
    category_names = []
    category_path_names = []

    tree = ET.parse(categories_file)
    root = tree.getroot()

    for child in root:
        cat_path = child.find("path")
        cat_path_ids = [cat.findtext("id") for cat in cat_path]
        cat_path_names = [cat.findtext("name") for cat in cat_path]
        leaf_id = cat_path_ids[-1]
        categories.append(leaf_id)
        category_names.append(cat_path_names[-1])
        category_path_names.append(" < ".join(reversed(cat_path_names)))

    df = pd.DataFrame(
        {
            "category": categories,
            "name": category_names,
            "path": category_path_names,
        },
    )

    print(df)
    df.to_pickle(categories_df_file)
    print(f"Saved categories df to {categories_df_file}")


# %%
punctuation_table = str.maketrans("", "", "®©™" + string.punctuation)
stemmer = nltk.stem.PorterStemmer()


def transform_query(text):
    text = text.lower()
    text = text.translate(punctuation_table)
    tokens = nltk.word_tokenize(text)
    tokens = [stemmer.stem(t) for t in tokens]
    return " ".join(tokens)


# %%
# Run prediction for a query and print top 10 category matches.
def predict(model, cats_df, query):
    print(f"query = {query}")
    query = transform_query(query)
    print(f"transformed query = {query}")

    p = model.predict(query, k=10)
    df = pd.DataFrame({"label": p[0], "score": p[1]})
    df["category"] = df.label.str.replace("__label__", "")
    df["name"] = df.category.map(cats_df.name)
    odf = df[["name", "score", "category"]]
    print(odf.to_string())
    print()

def predict_multiple(queries):
    cats_df = pd.read_pickle(categories_df_file).set_index("category")
    model = fasttext.load_model(model_file)
    for query in queries:
        predict(model, cats_df, query) 

# %%
# Sample command line:
# python predict.py ipad "ipad case" "apple laptop"
if __name__ == "__main__":
    if not Path(categories_df_file).exists():
        create_categories_df()

    predict_multiple(sys.argv[1:])