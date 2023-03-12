from collections import Counter
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Process some integers.')

args = parser.parse_args()
general = parser.add_argument_group("general")
general.add_argument("--input", default="/workspace/datasets/fasttext/labeled_products.txt", help="the file to read from")
general.add_argument("--output", default="/workspace/datasets/fasttext/pruned_labeled_products.txt", help="the file to output to")

args = parser.parse_args()
input_file = args.input
output_file = args.output

if __name__ == '__main__':
    products = []
    with open(input_file) as f:
        lines = f.readlines()
    for line in lines:
        products.append(line.split(" ", 1))
    c = Counter(product[0] for product in products)
    print(c)

    pruned_products = []
    for product in products:
        if c[product[0]] >= 500:
            pruned_products.append(product)
    print('product cnt before prune {}, after prune {}'.format(len(products), len(pruned_products)))
    with open(output_file, "w") as f:
        for product in pruned_products:
            f.write('{} {}'.format(product[0], product[1]))