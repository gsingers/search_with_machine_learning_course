"""
Creates a benchmark by predicting the most popular skus in each category
"""

from collections import defaultdict
import csv

wd = "../../data/downloaded/big/"

def get_popular_skus():
    """Returns a dictionary of the most popular skus in each category"""
    with open(wd + "train.csv") as infile:
        reader = csv.reader(infile, delimiter=",")
        reader.next() # burn the header

        categories = defaultdict(lambda: defaultdict(int))
        for (user, sku, category, query, click_time, query_time) in reader:
            categories[category][sku] += 1

        for category in categories:
            categories[category] = sorted(categories[category].items(), \
                                          key=lambda x: x[1])
            categories[category].reverse()
        return categories

def make_predictions(categories):
    """Write the predictions out"""
    with open(wd + "test.csv") as infile:
        reader = csv.reader(infile, delimiter=",")
        reader.next() # burn the header
        with open("popular_skus.csv", "w") as outfile:
            writer = csv.writer(outfile, delimiter=",")
            writer.writerow(["sku"])
            for (user, category, query, click_time, query_time) in reader:
                try:
                    guesses = [x[0] for x in categories[category][0:5]]
                    writer.writerow([" ".join(guesses)])
                except TypeError: # a category we haven't seen before
                    writer.writerow(["0"])

def main():
    """Creates the benchmark"""
    categories = get_popular_skus()
    make_predictions(categories)

if __name__ == "__main__":
    main()
