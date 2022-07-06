import csv
import os
import subprocess
from pathlib import Path

import fasttext
import pandas as pd
import requests
from sklearn.model_selection import train_test_split

ROOT = Path.cwd()
DIR = Path(ROOT, "week2")
DATA_DIR = Path(DIR, "data")
MODEL_DIR = Path(DIR, "models")
CONF_DIR = Path(DIR, "conf")
USER = os.environ["USER"]
PASS = os.environ["PASS"]

import sys

sys.path.append(DIR)

import logging

import pruneProducts as prune_products
from createContentTrainingData import transform_name

FORMAT = "%(name)s -- %(asctime)s -- %(message)s"
logger = logging.getLogger(__name__)
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)


def normalize_titles():
    titles = pd.read_csv(
        Path(DATA_DIR, "titles.txt"),
        sep="\t",
        header=None,
        names=["title"],
    )
    titles["normalized_title"] = titles["title"].apply(transform_name)
    titles[["normalized_title"]].to_csv(
        Path(DATA_DIR, "normalized_titles.txt"),
        header=False,
        index=False,
        sep="\t",
    )
    return None


def prepare_data(prune_n):
    logger.info("Base data pull")
    output_loc = Path(DATA_DIR, "labeled_products.txt")
    bash_command = (
        f"python week2/createContentTrainingData.py --output {output_loc}"
    )
    subprocess.run(bash_command, shell=True)

    logger.info("Extracting titles and pruning data")
    prune_products.main(prune_n)

    logger.info("Normalizing titles")
    normalize_titles()
    return None


def train_synonyms():
    # fit synonym model
    synonym_model = fasttext.train_unsupervised(
        f"{DATA_DIR}/normalized_titles.txt",
        epoch=25,
        minCount=20,
    )

    synonym_model.save_model(str(Path(MODEL_DIR, "title_model.bin")))
    return None


def generate_synonyms():
    # load titles
    titles = pd.read_csv(
        Path(DATA_DIR, "normalized_titles.txt"),
        sep="\t",
        header=None,
        names=["title"],
    )

    # join all words together in one list
    all_words = " ".join(titles["title"].tolist()).split(" ")

    # creater counter dictionary of unique words that are
    # greater than 4 chars in len
    counter = {}
    for word in set(all_words):
        if len(word) >= 4:
            counter[word] = 0

    # get word counts
    for aw in all_words:
        if aw in counter.keys():
            counter[aw] += 1

    # sort by count value
    counter = {
        k: v
        for k, v in sorted(
            counter.items(), reverse=True, key=lambda item: item[1]
        )
    }

    # output top 1000 words
    top_words = list(counter.keys())
    top_words = top_words[:1000]
    with open(f"{DATA_DIR}/top_words.txt", "w") as top_words_doc:
        for tw in top_words:
            top_words_doc.write(f"{tw}\n")
    top_words_doc.close()

    # load synonym model
    synonym_model = fasttext.load_model(
        str(Path(MODEL_DIR, "title_model.bin"))
    )

    # get synonyms
    synonyms = []
    for tw in top_words:
        nns = synonym_model.get_nearest_neighbors(tw)
        synonym_line = [tw]
        for nn in nns:
            if nn[0] > 0.8:
                synonym_line.append(nn[1])
        synonyms.append(synonym_line)

    # output synonyms
    with open(Path(DATA_DIR, "synonyms.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(synonyms)
    f.close()

    # mount in docker
    command = f"docker cp {DATA_DIR}/synonyms.csv opensearch-node1:/usr/share/opensearch/config/synonyms.csv"
    subprocess.run(command, shell=True)

    return None


def index_data():
    # delete first
    res = requests.delete(
        "https://localhost:9200/bbuy_products", verify=False, auth=(USER, PASS)
    )
    logger.info(f"Delete bbuy_products returned {res.status_code}")
    res = requests.delete(
        "https://localhost:9200/bbuy_queries", verify=False, auth=(USER, PASS)
    )
    logger.info(f"Delete bbuy_queries returned {res.status_code}")

    # index data
    queries_file_path = Path(CONF_DIR, "bbuy_queries.json")
    products_file_path = Path(CONF_DIR, "bbuy_products.json")
    command = (
        f"./index-data.sh -r -p {products_file_path} -q {queries_file_path}"
    )
    subprocess.run(command, shell=True)

    return None


def train_products(learning_rate, epochs):
    # shuffle, create train-test split
    logger.info("Shuffling and splitting data")
    data = pd.read_csv(
        Path(DATA_DIR, "pruned_labeled_products.txt"),
        sep="\t",
        header=None,
        names=["xml_str"],
    )
    train, test = train_test_split(
        data, test_size=0.1, random_state=42, shuffle=True
    )
    train[["xml_str"]].to_csv(
        Path(DATA_DIR, "pruned_train.txt"),
        header=False,
        index=False,
        sep="\t",
    )

    test[["xml_str"]].to_csv(
        Path(DATA_DIR, "pruned_test.txt"),
        header=False,
        index=False,
        sep="\t",
    )

    # train model
    logger.info("Training")
    model = fasttext.train_supervised(
        input=str(Path(DATA_DIR, "pruned_train.txt")),
        lr=learning_rate,
        epoch=epochs,
        wordNgrams=2,
    )

    # evaluate
    logger.info("Evaluating")
    for n in [1, 5, 10]:
        metrics = model.test(str(Path(DATA_DIR, "pruned_test.txt")), n)

        logger.info(" P@{} {:.3f}".format(n, metrics[1]))
        logger.info(" R@{} {:.3f}".format(n, metrics[2]))

    # save model
    model.save_model(str(Path(MODEL_DIR, "product_classifier.bin")))


def main(**kwargs):
    logger.info("Preparing data")
    prepare_data(kwargs["prune_n"])
    logger.info("Training product classifier")
    train_products(kwargs["product_lr"], kwargs["product_epochs"])
    logger.info("Fitting synonyms model")
    train_synonyms()
    logger.info("Generating synonyms")
    generate_synonyms()
    logger.info("Indexing data -- you will prompted to enter the password")
    index_data()
    logger.info("All done here")


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "--prune_n", help="Min n examples to prune to", default=500, type=int
    )
    parser.add_argument(
        "--product_lr",
        help="Learning rate for product classifier",
        default=0.6,
        type=float,
    )
    parser.add_argument(
        "--product_epochs",
        help="Number of epochs for product classifier",
        default=10,
        type=int,
    )
    args = parser.parse_args()

    main(**vars(args))
