import fasttext

model = fasttext.load_model('/workspace/datasets/fasttext/synonim_model.bin')
synonyms = open("/workspace/datasets/fasttext/synonyms.csv", 'w')

tr = 0.75

for w in open('/workspace/datasets/fasttext/top_words.txt', 'r').readlines():
    results = model.get_nearest_neighbors(w.replace('\n', ''))
    syns = [val[1] for val in results if val[0] >= tr]
    
    if len(syns) > 0:

        output = w.replace('\n', '')
        for syn in syns:
            output = output + ',' + syn
        output = output + '\n'
        synonyms.write(output)
