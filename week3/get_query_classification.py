import fasttext
import re
import nltk

stemmer = nltk.stem.PorterStemmer()


def clean_text(text):
    text = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)
    words = [stemmer.stem(word).strip() for word in text.split()]
    cleaned_text = " ".join(words)
    if text == "Beats By Dr. Dre- Monster Pro Over-the-Ear Headphones":
        print("Cleaning : {} : {}".format(text, cleaned_text))
    return cleaned_text


# Train model
model = fasttext.load_model("/workspace/datasets/fasttext/query_classification.bin")


def get_query_categories(query):
    categories, scores = model.predict(word, k=5)
    results = []
    for i, category in enumerate(categories):
        category = (category or "").replace("__label__", "")
        if scores[i] > 0.1:
            results.append(category)
    return results


queries = ["ipod", "sharp", "tv", "mobile", "iphone", "keurig", "laptop"]
for word in queries:
    print(get_query_categories(clean_text(word)))
