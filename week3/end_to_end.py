import csv
import os
import subprocess
from pathlib import Path

import fasttext
import pandas as pd

ROOT = Path.cwd()
DIR = Path(ROOT, "week3")
# DATA_DIR = Path(DIR, "data")
# MODEL_DIR = Path(DIR, "models")
# CONF_DIR = Path(DIR, "conf")
# USER = os.environ["USER"]
# PASS = os.environ["PASS"]

import sys

sys.path.append(DIR)

import logging

from create_labeled_queries import main as create_labeled_queries

FORMAT = "%(name)s -- %(asctime)s -- %(message)s"
LOGGER = logging.getLogger(__name__)
logging.basicConfig(format=FORMAT)
LOGGER.setLevel(logging.INFO)


def main(**kwargs):
    # create labeled queries / pruning as needed
    create_labeled_queries(kwargs["min_queries"], kwargs["labeled_data_fpath"])
    return None

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--min_queries", default=1, type=int)
    parser.add_argument("--labeled_data_fpath", default="/workspace/datasets/labeled_query_data.txt", type=str)

    args = parser.parse_args()

    main(**vars(args))