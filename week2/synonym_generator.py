import fasttext

model = fasttext.load_model('/workspace/datasets/fasttext/title_model.bin')

with open("/workspace/datasets/fasttext/top_words.txt") as input_file:
    with open("/workspace/datasets/fasttext/synonyms.csv", "w") as output:
        for line in input_file:
            array = [line.strip()]
            synonyms = [word for prob, word in model.get_nearest_neighbors(array[0]) if prob > 0.8]
            output_line_array = array + synonyms + ["\n"]
            output.write(",".join(output_line_array))