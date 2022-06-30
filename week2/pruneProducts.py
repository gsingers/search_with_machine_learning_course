from pathlib import Path

import pandas as pd

DATA_DIR = Path(".", "week2", "data") 


def split_xml(full_string):
    space_idx = full_string.find(" ")
    label = full_string[: space_idx]
    title = full_string[space_idx+1:]
    return (label, title)


def main(min_n):
    print("reading data")
    data = pd.read_csv(
        Path(DATA_DIR, "labeled_products.txt"),
        sep="\t",
        header=None,
        names=["xml_str"],
    )
    print(f"original nrows: {data.shape[0]}")

    print("splitting labels and titles")
    labels_titles = data["xml_str"].apply(split_xml)
    data["label"] = [lt[0] for lt in labels_titles]
    data["title"] = [lt[1] for lt in labels_titles]

    # get counts of each label
    print("counting labels")
    counter = (
        data.groupby("label")
        .agg({"label": "count"})
        .rename(columns={"label": "incidence"})
    )
    counter = counter.reset_index()

    # filter out labels with fewer than min_n examples
    print("filtering data")
    keep_labels = counter[counter["incidence"] >= min_n]
    filtered_data = data.merge(keep_labels, how="inner", on="label")
    print(f"filtered nrows: {filtered_data.shape[0]}")

    # output data
    print("outputting labeled products")
    filtered_data[["xml_str"]].to_csv(
        Path(DATA_DIR, "pruned_labeled_products.txt"),
        header=False,
        index=False,
        sep="\t",
    )

    print("outputting titles")
    data[["title"]].to_csv(
        Path(DATA_DIR, "titles.txt"),
        header=False,
        index=False,
        sep="\t",
    )
    
    return None


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--min_n", default=500, type=int)
    args = parser.parse_args()
    main(args.min_n)
