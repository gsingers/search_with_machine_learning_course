import fasttext

query = "subwoofer"
model = fasttext.load_model("/workspace/datasets/fasttext/query_classifier.bin")
query_cat = model.predict(query, k=2)[0][0].split("__")[2]
query_cat_score = model.predict(query)[1][0]
print(query_cat, query_cat_score)