import fasttext


def create_synonyms():
    model = fasttext.load_model('/workspace/datasets/fasttext/title_model.bin')

    with open('/workspace/datasets/fasttext/synonyms.csv', 'w') as fout:
        with open('/workspace/datasets/fasttext/top_words.txt', 'r') as fin:
            for word in fin:
                word = word.replace('\n', '')
                sinnonims = model.get_nearest_neighbors(word.replace('\n', ''), 20)
                fout.write(word)
                for score, sinn_word in sinnonims:
                    if score > 0.75:
                        fout.write(', ' + sinn_word)
                fout.write('\n')

if __name__ == '__main__':
    create_synonyms()