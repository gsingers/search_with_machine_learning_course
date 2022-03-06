import fasttext
import argparse

parser = argparse.ArgumentParser(description='Synonyms evaluation')
general = parser.add_argument_group("general")
general.add_argument("--input",
                     default="/workspace/datasets/fasttext/titles.txt",
                     help="the file to read synonyms from")
general.add_argument("--model",
                     default="cbow",
                     help="Default cbow, alternative skipgram")

general.add_argument("--minCount",
                     type=int,
                     default=5,
                     help="minimal number of word occurences [5]")
general.add_argument("--epoch",
                     type=int,
                     default=5,
                     help="number of epochs [5]")
general.add_argument("--minn",
                     type=int,
                     default=2,
                     help="min length of char ngram [2] ")
general.add_argument("--treshold",
                     type=float,
                     default=0.5,
                     help="treshold 0.5 ")
general.add_argument("--limit",
                     type=int,
                     default=3,
                     help="Limit no of samples 3 ")

args = parser.parse_args()
titles_file = args.input
model_name = args.model
minCount = args.minCount
epoch = args.epoch
minn = args.minn
treshold = args.treshold
limit = args.limit



model = fasttext.train_unsupervised(input=titles_file,
                                    model=model_name,
                                    minCount=minCount,
                                    epoch=epoch,
                                    minn=minn,
                                    )


brands = ["apple", "Sony", "Ubisoft", "Whirlpool", "Dell"]
product_types = ["Tablet", "Hard Drive",
                 "Notebook", "Smartphone", "Gaming Keyboard", "iPhone"]
models = ["VAIO", "Game Boy Advance", "Nikkor"]
attribute = ["4GB", "Black", "Windows", "MP3 Playback", '24"']

evaluate = [
    ("brands", brands),
    ("product types", product_types),
    ("models", models),
    ("attribute", attribute)
]


def main():
    from extractTitles import transform_training_data

    for (group_name, examples) in evaluate:
        print("{} \n".format(group_name), end='')
        for name in examples:
            name = transform_training_data(name)
            print(" {} \t ~> ".format(name.ljust(25)), end='')
            
            i = 0
            for (prob, synonym) in model.get_nearest_neighbors(name, k=100):
                i = i + 1
                if i > limit:
                    break

                if prob > treshold:
                    print("{} ({:.2f}%) \t".format(
                        synonym.ljust(15), prob*100), end='')
                

            print("\n", end='')


if __name__ == "__main__":
    main()
