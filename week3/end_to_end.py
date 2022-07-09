import csv
import logging
import sys
from pathlib import Path

import fasttext
import pandas as pd
from create_labeled_queries import main as create_labeled_queries
from sklearn.model_selection import train_test_split

ROOT = Path.cwd()
DIR = Path(ROOT, "week3")
DATA_DIR = Path(DIR, "data")
MODEL_DIR = Path(DIR, "models")

sys.path.append(DIR)

FORMAT = "%(name)s -- %(asctime)s -- %(message)s"
LOGGER = logging.getLogger(__name__)
logging.basicConfig(format=FORMAT)
LOGGER.setLevel(logging.INFO)


def main(**kwargs):
    # create labeled queries / pruning as needed
    LOGGER.info("Creating labeled queries")
    labeled_data_fpath = Path(DATA_DIR, "labeled_query_data.txt")
    create_labeled_queries(
        kwargs["min_queries"], labeled_data_fpath, kwargs["normalize_queries"]
    )

    # get train test split
    LOGGER.info("Splitting into train and test data")
    data = pd.read_csv(
        labeled_data_fpath,
        names=["output", "category"],
        sep="|",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
    )
    if kwargs["min_queries"] != 1:
        # stratify by category if possible
        # only possible where there are 2 or more values per category
        cat_map = {
            cat: e for e, cat in enumerate(data["category"].unique().tolist())
        }
        data["cat_id"] = data["category"].map(cat_map)
        train, test = train_test_split(
            data,
            test_size=0.1,
            random_state=42,
            shuffle=True,
            stratify=data["cat_id"],
        )
    else:
        train, test = train_test_split(
            data, test_size=0.1, random_state=42, shuffle=True
        )

    train[["output"]].to_csv(
        Path(DATA_DIR, "train.txt"),
        header=False,
        sep="|",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
        index=False,
    )
    test[["output"]].to_csv(
        Path(DATA_DIR, "test.txt"),
        header=False,
        sep="|",
        escapechar="\\",
        quoting=csv.QUOTE_NONE,
        index=False,
    )

    # train model
    LOGGER.info("Training")
    model = fasttext.train_supervised(
        input=str(Path(DATA_DIR, "train.txt")),
        lr=kwargs["learning_rate"],
        epoch=kwargs["epochs"],
    )

    # evaluate model
    LOGGER.info("Evaluating")
    for n in [1, 3, 5]:
        metrics = model.test(str(Path(DATA_DIR, "test.txt")), n)

        LOGGER.info(" P@{} {:.3f}".format(n, metrics[1]))
        LOGGER.info(" R@{} {:.3f}".format(n, metrics[2]))

    # save model
    model.save_model(str(Path(MODEL_DIR, "query_classifier.bin")))

    return None


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()

    create_queries = parser.add_argument_group("create_queries")
    create_queries.add_argument("--min_queries", default=1, type=int)
    create_queries.add_argument(
        "--normalize_queries",
        default=False,
        action="store_true",
        help="whether to normalize queries",
    )

    train_classifier = parser.add_argument_group("train_classifier")
    train_classifier.add_argument("--epochs", default=5, type=int)
    train_classifier.add_argument("--learning_rate", default=1.0, type=float)

    args = parser.parse_args()
    print(args)

    main(**vars(args))
