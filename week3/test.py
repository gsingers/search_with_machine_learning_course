import fasttext

model = fasttext.load_model("/workspace/datasets/fasttext/query_classifier.bin")
query_cat = model.predict("lcd tv", k=2)[0][0].split("__")[2]
query_cat_score = model.predict("hp touchpad")[1][0]
print(query_cat, query_cat_score)