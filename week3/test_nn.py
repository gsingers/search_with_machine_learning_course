import fasttext
import re
from nltk.stem import SnowballStemmer
stemmer = SnowballStemmer('english')


def transform_word(name):
    name = name.replace('\n', ' ')
    name = re.sub("[^0-9a-zA-Z]+", " ", name).lower()
    return stemmer.stem(name)


if __name__ == '__main__':
    with open('test_nn') as f:
        words = f.readlines()
    words = [transform_word(w.strip()) for w in words]

    model = fasttext.load_model('title_model.bin')
    for word in words:
        synonyms = [f"{s[1]} ({round(s[0],2)})" for s in model.get_nearest_neighbors(word) if s[0]>0]
        print(f"{word} : {synonyms}")
