import fasttext

model = fasttext.load_model("/workspace/datasets/fasttext/title_model_100.bin")

with open('/workspace/datasets/fasttext/top_words.txt') as top_words:
    with open('/workspace/datasets/fasttext/synonyms.csv', 'w') as out:
        for word in top_words:
            word_stripped = word.strip()
            synonyms = ",".join([word_stripped] + [x[1] for x in model.get_nearest_neighbors(word_stripped) if x[0] >= 0.75])
            out.write(synonyms + "\n")
