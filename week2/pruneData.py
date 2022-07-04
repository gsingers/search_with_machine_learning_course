import pandas as pd 
import numpy as np

df = pd.read_table("/workspace/datasets/fasttext/labeled_products.txt", header=None)

labels = []
for idx, row in df.iterrows():
    labels.append(row[0].split()[0])

df["label"] = labels

COUNT = 500
count_labels = df.groupby("label").size().sort_values().reset_index()
count_labels.columns = ["label", "count"]
filtered_data = count_labels.loc[count_labels["count"] > COUNT, :]["label"]

filtered_data_df = df.loc[df.label.isin(filtered_data), 0]
np.savetxt("/workspace/datasets/fasttext/pruned_labeled_products.txt", filtered_data_df.values, "%s")