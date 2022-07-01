import fasttext

model = fasttext.load_model("/workspace/datasets/fasttext/title_model.bin")

def create_synonyms():
    with open('/workspace/datasets/fasttext/top_words.txt', 'r') as f:
        with open('/workspace/datasets/fasttext/synonyms.csv', 'w') as wf:
            for syn in f:
                syn = syn.rstrip()
                pred = model.get_nearest_neighbors(syn, 10, '0.8')
                synonyms = ''
                for neighbor in pred:

                    synonyms = synonyms + ','
                    synonyms = synonyms + neighbor[1]

                wf.write(syn +synonyms + '\n')


            


if __name__ == "__main__":
    create_synonyms()