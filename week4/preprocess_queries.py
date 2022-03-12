# %%
import pandas as pd
import string
import nltk
from tqdm.auto import tqdm

tqdm.pandas()


# %%
queries_file_name = r"/workspace/datasets/train.csv"
query_df_filename = "/workspace/datasets/week4/query_df.pk"


# %%
# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
print(f"Reading query data from {queries_file_name}")
df = pd.read_csv(queries_file_name)[["category", "query"]].rename(
    columns={
        "query": "raw_query",
    }
)


# %%
punctuation_table = str.maketrans("", "", "®©™" + string.punctuation)
stemmer = nltk.stem.PorterStemmer()


def transform_query(text):
    text = text.lower()
    text = text.translate(punctuation_table)
    tokens = nltk.word_tokenize(text)
    tokens = [stemmer.stem(t) for t in tokens]
    return " ".join(tokens)

print("Preprocessing query data")
tdf = df.assign(
    query=df["raw_query"].progress_map(transform_query),
)

print(tdf)
print(f"Saving preprocessed query data to {query_df_filename}")
pd.to_pickle(tdf, query_df_filename)
