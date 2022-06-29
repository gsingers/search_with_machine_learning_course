import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DATA_DIR = Path(".", "week2", "data")


def split_label(full_string):
    return full_string[: full_string.find(" ")]


def main(min_n):
    logger.info("reading data")
    data = pd.read_csv(
        Path(DATA_DIR, "labeled_products.txt"),
        sep="\t",
        header=None,
        names=["xml_str"],
        nrows=5000,
    )

    logger.info("extracting label")
    data["label"] = data["xml_str"].apply(split_label)

    # get counts of each label
    logger.info("counting labels")
    counter = (
        data.groupby("label")
        .agg({"label": "count"})
        .rename(columns={"label": "incidence"})
    )
    counter = counter.reset_index()

    # filter out labels with fewer than min_n examples
    logger.info("filtering data")
    keep_labels = counter[counter["incidence"] >= min_n]
    filtered_data = data.merge(keep_labels, how="inner", on="label")

    # output data
    logger.info("outputting data")
    filtered_data.to_csv(Path(DATA_DIR, "pruned_labeled_products.txt"))
    return None


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser
    parser.add_argument("--min_n", default=500, type=int)
    args = parser.parse_args()
    main(args.min_n)
