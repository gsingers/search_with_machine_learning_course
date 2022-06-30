import click
import fasttext
import sys

@click.command()
@click.option("--threshold", default=0.75)
@click.argument("model_name")
def find_synonyms(model_name, threshold):
    model = fasttext.FastText.load_model(model_name)
    for line in sys.stdin:
        line = line.strip()
        neighbors = model.get_nearest_neighbors(line)
        strong_neighbors = [syn for score,syn in neighbors if score > threshold]
        print(','.join((line, *strong_neighbors)))

if __name__ == '__main__':
    find_synonyms()
