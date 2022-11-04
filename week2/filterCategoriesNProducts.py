import logging
from pathlib import Path
import pandas as pd
logging.basicConfig(level=logging.INFO)

def read_data(path:str) -> pd.DataFrame:
    product_data = pd.read_csv(
        path,
        sep="§§§", # a never occurring sep
        header=None,
        names=['product_data']
    ) 
    return product_data


def filter_data(df:pd.DataFrame, n:int = 500) -> pd.DataFrame:
    df['cat'] = df['product_data'].apply(lambda x: x.split()[0])
    cat_counts = df['cat'].value_counts()
    cat_above_n = cat_counts[cat_counts >+ n].index
    filtered_df = df[df['cat'].isin(cat_above_n)]
    return filtered_df['product_data']


def save_data(df:pd.DataFrame, path:str) -> None:
    df.to_csv(path, header=False, index=False,)
    return None


load_path = "/workspace/datasets/fasttext/labeled_products.txt"
save_path = "/workspace/datasets/fasttext/pruned_labeled_products.txt"
min_count = 500

if __name__ == "__main__":
    logging.info(f"Reading file from {load_path}...")
    df = read_data(load_path)
    logging.info(f"Filtering to categories equal or above {min_count} counts...")
    filtered_df = filter_data(df, min_count)
    logging.info(f"Saving file with {filtered_df.shape[0]} entries to {save_path}...")
    save_data(filtered_df, save_path)
    logging.info(f"File saved in {save_path}.")
