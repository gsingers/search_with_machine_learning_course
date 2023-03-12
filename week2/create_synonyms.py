import fasttext

threshold = 0.75

def get_synonyms():
    model = fasttext.load_model("/workspace/datasets/fasttext/title_model.bin")

    write_stream = open("/workspace/datasets/fasttext/synonyms.csv", "w")
    
    with open('/workspace/datasets/fasttext/top_words.txt', 'r') as read_stream:
        for word in read_stream:
            word = word.rstrip('\n')
            all_nn = model.get_nearest_neighbors(word)
            all_nn = [name for score, name in all_nn if score > threshold]
            valid_nn = ','.join((word, *all_nn))
            write_stream.write(valid_nn + '\n')

    write_stream.close()            



if __name__ == '__main__':
    get_synonyms()