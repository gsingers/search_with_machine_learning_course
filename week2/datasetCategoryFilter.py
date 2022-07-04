import argparse
import pandas

parser = argparse.ArgumentParser(description='Filter categories by number of products.')
parser.add_argument("--input", default='/workspace/datasets/fasttext/labeled_products.txt',  help="the input filepath", type=str)
parser.add_argument("--output", default='/workspace/datasets/fasttext/pruned_labeled_products.txt', help="the output filepath", type=str)
parser.add_argument("--min_samples", default=500,  help="Categories with less than min_samples will be disconsidered", type=int)


def get_arguments():
    args = parser.parse_args()
    min_filter = args.min_samples
    inputFile = args.input
    outputFile = args.output
    return input_file, output_file, min_filter_cut


input_file, output_file, min_filter_cut = get_arguments()
df = pandas.read_csv(input_file)
df = df.str.str.split(' ', n=1, expand=True).groupby(axis=0).filter(lambda x: len(x) >= min_filter_cut)
df.to_csv(outputFile, sep='\t', header=None, index=False) 