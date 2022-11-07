import fasttext

model = fasttext.load_model("/workspace/datasets/fasttext/title_model_normalized.bin")
title_file = open("/workspace/datasets/fasttext/top_words.txt", "r")
synonyms = open("/workspace/datasets/fasttext/synonyms.csv", "w")
threshold = 0.8

for word in title_file.readlines():
    #print (word)
    word = word.replace('\n', '')
    neighbor_list = []
    neighbors = model.get_nearest_neighbors(word)
    #print (neighbors)
    for score, neighbor in neighbors:
        if score > threshold:
            neighbor_list.append(neighbor)
    if len(neighbor_list) > 0:
        synonyms.write(word + "," + ",".join(neighbor_list) + '\n')

