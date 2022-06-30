import subprocess
import fasttext

from pathlib import Path
import pandas as pd
import csv

from sklearn.model_selection import train_test_split

DIR = Path(".", "week2")
DATA_DIR = Path(DIR, "data") 

import sys
sys.path.append(DIR)

import pruneProducts as prune_products
from createContentTrainingData import transform_name

import logging
logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

def print_results(N, p, r):
    print("N\t" + str(N))
    print("P@{}\t{:.3f}".format(1, p))
    print("R@{}\t{:.3f}".format(1, r))

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

def prepare_data():
    logger.info("Base data pull")
    output_loc = Path(DATA_DIR, "labeled_products.txt")
    bash_command = f"python week2/createContentTrainingData.py --output {output_loc}"
    # subprocess.run(bash_command, shell=True)

    logger.info("Extracting titles and pruning data")
    prune_products.main(500)

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

    synonym_model.save_model(str(Path(DIR, "title_model.bin")))
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
    counter = {k: v for k, v in sorted(counter.items(), reverse=True, key=lambda item: item[1])}

    # output top 1000 words
    top_words = list(counter.keys())
    top_words = top_words[:1000]
    with open(f"{DATA_DIR}/top_words.txt", "w") as top_words_doc:
        for tw in top_words:
                top_words_doc.write(f"{tw}\n")
    top_words_doc.close()

    # load synonym model
    synonym_model = fasttext.load_model(str(Path(DIR, "title_model.bin")))
    
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

    return None

def search_model():

    # shuffle, create train-test split
    logger.info("Shuffling and splitting")
    data = pd.read_csv(
        Path(DATA_DIR, "pruned_labeled_products.txt"),
        sep="\t",
        header=None,
        names=["xml_str"],
    )
    train, test = train_test_split(data, test_size=.1, random_state=42, shuffle=True)
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
        input="week2/data/pruned_train.txt",
        lr=0.8,
        epoch=25,
        wordNgrams=2,
    )

    # evaluate
    logger.info("Evaluating")
    print_results(*model.test("week2/data/pruned_test.txt"))

def main():
    logger.info("Preparing data")
    prepare_data()
    logger.info("Fitting synonyms model")
    train_synonyms()
    logger.info("Generating synonyms")
    generate_synonyms()


if __name__ == "__main__":
    main()