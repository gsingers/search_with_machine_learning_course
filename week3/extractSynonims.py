import fasttext

list_words=['iphone','headphones','headset','cooktop','cartridge', 'sony','samsung','apple','lenovo','dell','thinkpad', 'idealab','macbook', 'envy','pavilion','black','yellow','red','blue','green']
THRESHOLD=0.70

syns_model = fasttext.load_model('/workspace/datasets/fasttext/title_model.bin')
for w in list_words:
    
    #syn = syns_model.get_nearest_neighbors(w) if score > THRESHOLD
    print ('Synonyms for ' +w)
    syn = syns_model.get_nearest_neighbors(w)
    #print(syn)
    for s in syn:
        if s[0]>THRESHOLD:
            print(s[1])
    print()
    
    


