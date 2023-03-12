import fasttext

model = fasttext.load_model('title_model.bin')
input_file = '/workspace/datasets/fasttext/top_words.txt'
output_file = '/workspace/datasets/fasttext/synonyms.csv'
threshold = 0.75


if __name__ == '__main__':
    with open(input_file) as reader:
        with open(output_file, 'w') as writer:
            for w in reader.readlines():
                w = w.strip()
                synonyms = [nn[1] for nn in model.get_nearest_neighbors(w) if nn[0] >= threshold]
                if synonyms:
                    writer.write('{},{}\n'.format(w, ','.join(synonyms)))