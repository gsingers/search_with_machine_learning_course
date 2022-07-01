from pathlib import Path
import logging

import pandas as pd

DATA_DIR = Path(".", "week2", "data") 

pplogger = logging.getLogger(__name__)
pplogger.setLevel(logging.INFO)

def split_xml(full_string):
    space_idx = full_string.find(" ")
    label = full_string[: space_idx]
    title = full_string[space_idx+1:]
    return (label, title)


def main(min_n):
    pplogger.info("reading data")
    data = pd.read_csv(
        Path(DATA_DIR, "labeled_products.txt"),
        sep="\t",
        header=None,
        names=["xml_str"],
    )
    pplogger.info(f"original nrows: {data.shape[0]}")

    pplogger.info("splitting labels and titles")
    labels_titles = data["xml_str"].apply(split_xml)
    data["label"] = [lt[0] for lt in labels_titles]
    data["title"] = [lt[1] for lt in labels_titles]

    # get counts of each label
    pplogger.info("counting labels")
    counter = (
        data.groupby("label")
        .agg({"label": "count"})
        .rename(columns={"label": "incidence"})
    )
    counter = counter.reset_index()

    # filter out labels with fewer than min_n examples
    pplogger.info("filtering data")
    keep_labels = counter[counter["incidence"] >= min_n]
    filtered_data = data.merge(keep_labels, how="inner", on="label")
    pplogger.info(f"filtered nrows: {filtered_data.shape[0]}")

    # output data
    pplogger.info("outputting labeled products")
    filtered_data[["xml_str"]].to_csv(
        Path(DATA_DIR, "pruned_labeled_products.txt"),
        header=False,
        index=False,
        sep="\t",
    )

    pplogger.info("outputting titles")
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
