vimport pandas as pd 
import numpy as np

# filter product categories with at least 500 products, output to csv
df = pd.read_table("/workspace/datasets/fasttext/labeled_products.txt", header=None)

labels = []
for idx, row in df.iterrows():
    labels.append(row[0].split()[0])

df["label"] = labels

_MIN_COUNT = 500
labels_by_size = df.groupby("label").size().sort_values().reset_index()
labels_by_size.columns = ["label", "count"]
labels_large = labels_by_size.loc[labels_by_size["count"] > _MIN_COUNT, :]["label"]

df_large_labels = df.loc[df.label.isin(labels_large), 0]
np.savetxt("/workspace/datasets/fasttext/pruned_labeled_products.txt", df_large_labels.values, "%s")